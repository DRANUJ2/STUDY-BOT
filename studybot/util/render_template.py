import os
import re
from pathlib import Path
from typing import Dict, Any, Optional

class TemplateRenderer:
    """Simple template renderer for HTML templates"""
    
    def __init__(self, template_dir: str = "templates"):
        """
        Initialize template renderer
        
        Args:
            template_dir (str): Directory containing templates
        """
        self.template_dir = Path(template_dir)
        self.cache = {}
    
    def render(self, template_name: str, context: Dict[str, Any] = None) -> str:
        """
        Render a template with given context
        
        Args:
            template_name (str): Name of the template file
            context (Dict[str, Any], optional): Context variables
            
        Returns:
            str: Rendered HTML content
        """
        if context is None:
            context = {}
        
        # Get template content
        template_content = self._get_template(template_name)
        
        # Render template
        return self._render_content(template_content, context)
    
    def _get_template(self, template_name: str) -> str:
        """
        Get template content from file or cache
        
        Args:
            template_name (str): Template name
            
        Returns:
            str: Template content
        """
        # Check cache first
        if template_name in self.cache:
            return self.cache[template_name]
        
        # Load template from file
        template_path = self.template_dir / template_name
        
        if not template_path.exists():
            raise FileNotFoundError(f"Template not found: {template_name}")
        
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Cache template
        self.cache[template_name] = content
        return content
    
    def _render_content(self, content: str, context: Dict[str, Any]) -> str:
        """
        Render template content with context
        
        Args:
            content (str): Template content
            context (Dict[str, Any]): Context variables
            
        Returns:
            str: Rendered content
        """
        # Replace variables {{ variable }}
        for key, value in context.items():
            placeholder = f"{{{{ {key} }}}}"
            if isinstance(value, (str, int, float, bool)):
                content = content.replace(placeholder, str(value))
        
        # Handle conditional statements {% if condition %}...{% endif %}
        content = self._handle_conditionals(content, context)
        
        # Handle loops {% for item in items %}...{% endfor %}
        content = self._handle_loops(content, context)
        
        return content
    
    def _handle_conditionals(self, content: str, context: Dict[str, Any]) -> str:
        """
        Handle conditional statements in template
        
        Args:
            content (str): Template content
            context (Dict[str, Any]): Context variables
            
        Returns:
            str: Processed content
        """
        # Pattern for {% if condition %}...{% endif %}
        if_pattern = r'{%\s*if\s+(\w+)\s*%}(.*?){%\s*endif\s*%}'
        
        def replace_if(match):
            condition = match.group(1)
            content_block = match.group(2)
            
            # Check if condition is true in context
            if self._evaluate_condition(condition, context):
                return content_block
            else:
                return ""
        
        return re.sub(if_pattern, replace_if, content, flags=re.DOTALL)
    
    def _handle_loops(self, content: str, context: Dict[str, Any]) -> str:
        """
        Handle loop statements in template
        
        Args:
            content (str): Template content
            context (Dict[str, Any]): Context variables
            
        Returns:
            str: Processed content
        """
        # Pattern for {% for item in items %}...{% endfor %}
        for_pattern = r'{%\s*for\s+(\w+)\s+in\s+(\w+)\s*%}(.*?){%\s*endfor\s*%}'
        
        def replace_for(match):
            item_var = match.group(1)
            items_var = match.group(2)
            content_block = match.group(3)
            
            # Get items from context
            items = context.get(items_var, [])
            
            if not isinstance(items, (list, tuple)):
                return ""
            
            # Render content for each item
            result = ""
            for item in items:
                # Create new context with item
                item_context = context.copy()
                item_context[item_var] = item
                
                # Render content block with item context
                item_content = self._render_content(content_block, item_context)
                result += item_content
            
            return result
        
        return re.sub(for_pattern, replace_for, content, flags=re.DOTALL)
    
    def _evaluate_condition(self, condition: str, context: Dict[str, Any]) -> bool:
        """
        Evaluate a condition string
        
        Args:
            condition (str): Condition to evaluate
            context (Dict[str, Any]): Context variables
            
        Returns:
            bool: True if condition is met
        """
        # Simple condition evaluation
        if condition in context:
            value = context[condition]
            if isinstance(value, bool):
                return value
            elif isinstance(value, (str, list, dict)):
                return bool(value)
            elif isinstance(value, (int, float)):
                return value != 0
            else:
                return bool(value)
        
        return False
    
    def clear_cache(self):
        """Clear template cache"""
        self.cache.clear()
    
    def reload_template(self, template_name: str):
        """
        Reload a specific template from file
        
        Args:
            template_name (str): Name of template to reload
        """
        if template_name in self.cache:
            del self.cache[template_name]

# Global template renderer instance
template_renderer = TemplateRenderer()

def render_template(template_name: str, context: Dict[str, Any] = None) -> str:
    """
    Convenience function to render templates
    
    Args:
        template_name (str): Name of template to render
        context (Dict[str, Any], optional): Context variables
        
    Returns:
        str: Rendered HTML content
    """
    return template_renderer.render(template_name, context)

def render_download_template(file_info: Dict[str, Any]) -> str:
    """
    Render download template with file information
    
    Args:
        file_info (Dict[str, Any]): File information dictionary
        
    Returns:
        str: Rendered HTML content
    """
    context = {
        'file_name': file_info.get('file_name', 'Unknown'),
        'file_size': file_info.get('file_size', 'Unknown'),
        'upload_date': file_info.get('upload_date', 'Unknown'),
        'file_type': file_info.get('file_type', 'Unknown'),
        'file_description': file_info.get('description', ''),
        'download_link': file_info.get('download_link', '#')
    }
    
    return render_template('dl.html', context)

def render_request_template() -> str:
    """
    Render request template
    
    Returns:
        str: Rendered HTML content
    """
    return render_template('req.html', {})

def render_custom_template(template_name: str, **kwargs) -> str:
    """
    Render custom template with keyword arguments
    
    Args:
        template_name (str): Name of template to render
        **kwargs: Context variables
        
    Returns:
        str: Rendered HTML content
    """
    return render_template(template_name, kwargs)
