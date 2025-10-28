#!/usr/bin/env python3
"""
Sistema de cache inteligente para dados do GitHub.
"""
import json
import pickle
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
import yaml


class CacheManager:
    """Sistema de cache inteligente para dados do GitHub."""
    
    def __init__(self, cache_dir: str = "logs/cache", ttl_hours: Dict[str, int] = None):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        
        # TTL por tipo de dados (em horas)
        self.ttl_hours = ttl_hours or {
            'projects': 24,      # Projetos mudam raramente
            'repositories': 6,   # Repositórios mudam ocasionalmente
            'issues': 1,         # Issues mudam frequentemente
            'labels': 12,        # Labels mudam ocasionalmente
            'state': 0.5         # Estado de processamento (30 min)
        }
    
    def _get_cache_path(self, cache_type: str, key: str = None) -> Path:
        """Gera caminho do arquivo de cache."""
        if key:
            # Hash da chave para evitar caracteres inválidos
            key_hash = hashlib.md5(key.encode()).hexdigest()[:8]
            return self.cache_dir / f"{cache_type}_{key_hash}.json"
        return self.cache_dir / f"{cache_type}.json"
    
    def _is_expired(self, cache_path: Path, ttl_hours: int) -> bool:
        """Verifica se o cache expirou."""
        if not cache_path.exists():
            return True
        
        file_time = datetime.fromtimestamp(cache_path.stat().st_mtime)
        expiry_time = file_time + timedelta(hours=ttl_hours)
        return datetime.now() > expiry_time
    
    def get(self, cache_type: str, key: str = None) -> Optional[Dict[str, Any]]:
        """Recupera dados do cache."""
        cache_path = self._get_cache_path(cache_type, key)
        ttl_hours = self.ttl_hours.get(cache_type, 1)
        
        if self._is_expired(cache_path, ttl_hours):
            return None
        
        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                print(f"📦 Cache hit: {cache_type}" + (f" ({key})" if key else ""))
                return data
        except (json.JSONDecodeError, FileNotFoundError):
            return None
    
    def set(self, cache_type: str, data: Dict[str, Any], key: str = None) -> None:
        """Armazena dados no cache."""
        cache_path = self._get_cache_path(cache_type, key)
        
        try:
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False, default=str)
            print(f"💾 Cache stored: {cache_type}" + (f" ({key})" if key else ""))
        except Exception as e:
            print(f"⚠️  Erro ao salvar cache {cache_type}: {e}")
    
    def invalidate(self, cache_type: str, key: str = None) -> None:
        """Invalida cache específico."""
        cache_path = self._get_cache_path(cache_type, key)
        if cache_path.exists():
            cache_path.unlink()
            print(f"🗑️  Cache invalidated: {cache_type}" + (f" ({key})" if key else ""))
    
    def clear_all(self) -> None:
        """Limpa todo o cache."""
        for cache_file in self.cache_dir.glob("*.json"):
            cache_file.unlink()
        print("🧹 Cache limpo completamente")
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do cache."""
        stats = {
            'total_files': 0,
            'total_size': 0,
            'by_type': {},
            'expired_files': 0
        }
        
        for cache_file in self.cache_dir.glob("*.json"):
            stats['total_files'] += 1
            stats['total_size'] += cache_file.stat().st_size
            
            # Extrair tipo do nome do arquivo
            cache_type = cache_file.stem.split('_')[0]
            if cache_type not in stats['by_type']:
                stats['by_type'][cache_type] = 0
            stats['by_type'][cache_type] += 1
            
            # Verificar se expirou
            ttl_hours = self.ttl_hours.get(cache_type, 1)
            if self._is_expired(cache_file, ttl_hours):
                stats['expired_files'] += 1
        
        return stats


class IssueProcessingState:
    """Gerencia estado de processamento de issues."""
    
    def __init__(self, cache_manager: CacheManager):
        self.cache_manager = cache_manager
        self.state_key = "issue_processing_state"
    
    def get_processed_issues(self, repo_name: str) -> Dict[str, Dict[str, Any]]:
        """Recupera issues já processados de um repositório."""
        state = self.cache_manager.get(self.state_key, repo_name) or {}
        return state.get('processed_issues', {})
    
    def mark_issue_processed(self, repo_name: str, issue_id: str, 
                           issue_data: Dict[str, Any]) -> None:
        """Marca issue como processado."""
        state = self.cache_manager.get(self.state_key, repo_name) or {}
        if 'processed_issues' not in state:
            state['processed_issues'] = {}
        
        state['processed_issues'][issue_id] = {
            'processed_at': datetime.now().isoformat(),
            'issue_data': issue_data
        }
        
        self.cache_manager.set(self.state_key, state, repo_name)
    
    def get_issue_hash(self, issue_data: Dict[str, Any]) -> str:
        """Gera hash único para issue baseado em dados relevantes."""
        # Campos que indicam mudança no issue
        relevant_fields = {
            'id': issue_data.get('id'),
            'state': issue_data.get('state'),
            'closedAt': issue_data.get('closedAt'),
            'updatedAt': issue_data.get('updatedAt'),
            'projectItems': issue_data.get('projectItems', {}).get('nodes', [])
        }
        
        # Gerar hash dos campos relevantes
        hash_string = json.dumps(relevant_fields, sort_keys=True)
        return hashlib.md5(hash_string.encode()).hexdigest()
    
    def has_issue_changed(self, repo_name: str, issue_id: str, 
                         current_issue_data: Dict[str, Any]) -> bool:
        """Verifica se issue mudou desde último processamento."""
        processed_issues = self.get_processed_issues(repo_name)
        
        if issue_id not in processed_issues:
            return True  # Issue não foi processado antes
        
        stored_data = processed_issues[issue_id]['issue_data']
        current_hash = self.get_issue_hash(current_issue_data)
        stored_hash = self.get_issue_hash(stored_data)
        
        return current_hash != stored_hash


def cleanup_expired_cache(cache_manager: CacheManager) -> None:
    """Limpa cache expirado automaticamente."""
    stats = cache_manager.get_stats()
    if stats['expired_files'] > 10:
        print(f"🧹 Limpando {stats['expired_files']} arquivos de cache expirados...")
        cache_manager.clear_all()


def log_cache_stats(cache_manager: CacheManager) -> None:
    """Log de estatísticas de cache."""
    stats = cache_manager.get_stats()
    print(f"📊 Cache: {stats['total_files']} arquivos, "
          f"{stats['total_size']/1024:.1f}KB, "
          f"{stats['expired_files']} expirados")
