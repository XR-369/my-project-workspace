from enum import Enum
from textnode import TextNode, TextType, text_node_to_html_node
from htmlnode import HTMLNode, LeafNode, ParentNode

class BlockType(Enum):
    PARAGRAPH = "paragraph"
    HEADING = "heading"
    CODE = "code"
    QUOTE = "quote"
    UNORDERED_LIST = "unordered_list"
    ORDERED_LIST = "ordered_list"

def markdown_to_blocks(markdown):
    """Split markdown document into blocks separated by blank lines"""
    normalized_markdown = markdown.replace('\r\n', '\n').replace('\r', '\n')
    blocks = normalized_markdown.split("\n\n")
    processed_blocks = []
    for block in blocks:
        stripped_block = block.strip()
        if stripped_block:
            processed_blocks.append(stripped_block)
    return processed_blocks

def block_to_block_type(block):
    """Determine the type of a markdown block"""
    lines = block.split('\n')
    
    if block.startswith(('# ', '## ', '### ', '#### ', '##### ', '###### ')):
        return BlockType.HEADING
    
    # FIXED: Handle both single-line and multi-line code blocks
    if len(lines) >= 1:
        first_line_clean = lines[0].strip()
        last_line_clean = lines[-1].strip()
        
        # For single-line blocks, check if entire block is wrapped in ```
        if len(lines) == 1:
            if (first_line_clean.startswith('```') and 
                first_line_clean.endswith('```') and
                len(first_line_clean) > 6):  # Make sure there's content between ```
                return BlockType.CODE
        # For multi-line blocks, check if first line starts with ``` and last line equals ```
        else:
            if (first_line_clean.startswith('```') and 
                last_line_clean == '```'):
                return BlockType.CODE
    
    if all(line.startswith('>') for line in lines):
        return BlockType.QUOTE
    
    if all(line.startswith('- ') for line in lines):
        return BlockType.UNORDERED_LIST
    
    if len(lines) > 0:
        is_ordered = True
        for i, line in enumerate(lines):
            expected_prefix = f"{i+1}. "
            if not line.startswith(expected_prefix):
                is_ordered = False
                break
        if is_ordered:
            return BlockType.ORDERED_LIST
    
    return BlockType.PARAGRAPH

def text_to_children(text):
    """Convert markdown text to a list of HTMLNodes for inline elements"""
    from text_processing import text_to_textnodes
    text_nodes = text_to_textnodes(text)
    html_nodes = []
    for text_node in text_nodes:
        html_node = text_node_to_html_node(text_node)
        html_nodes.append(html_node)
    return html_nodes

def heading_to_html(block):
    """Convert heading block to HTMLNode"""
    level = 0
    for char in block:
        if char == '#':
            level += 1
        else:
            break
    
    content = block[level:].strip()
    children = text_to_children(content)
    return ParentNode(f"h{level}", children)

def code_to_html(block):
    """Convert code block to HTMLNode"""
    lines = block.split('\n')
    
    # Handle single-line code blocks (```code```)
    if len(lines) == 1:
        content = lines[0][3:-3].strip()  # Remove triple backticks from start and end
    else:
        # Multi-line code blocks - remove first and last lines (the triple backticks)
        content_lines = lines[1:-1] if len(lines) > 2 else ['']
        content = '\n'.join(content_lines)
    
    # Add trailing newline for multi-line blocks to match test expectation
    if len(lines) > 1 and content and not content.endswith('\n'):
        content += '\n'
    
    # For code blocks, don't parse inline markdown - treat as raw text
    code_node = LeafNode("code", content)
    return ParentNode("pre", [code_node])

def quote_to_html(block):
    """Convert quote block to HTMLNode"""
    lines = block.split('\n')
    # Remove > from each line and strip, then join with spaces
    content_lines = [line[1:].strip() for line in lines]
    content = ' '.join(content_lines)
    children = text_to_children(content)
    return ParentNode("blockquote", children)

def unordered_list_to_html(block):
    """Convert unordered list block to HTMLNode"""
    lines = block.split('\n')
    list_items = []
    for line in lines:
        # Remove "- " from start and convert content
        content = line[2:].strip()
        children = text_to_children(content)
        list_items.append(ParentNode("li", children))
    return ParentNode("ul", list_items)

def ordered_list_to_html(block):
    """Convert ordered list block to HTMLNode"""
    lines = block.split('\n')
    list_items = []
    for line in lines:
        # Remove "X. " from start (where X is the number)
        content = line.split('. ', 1)[1].strip()
        children = text_to_children(content)
        list_items.append(ParentNode("li", children))
    return ParentNode("ol", list_items)

def paragraph_to_html(block):
    """Convert paragraph block to HTMLNode"""
    # Join lines with spaces to remove internal newlines
    content = ' '.join(block.split('\n'))
    children = text_to_children(content)
    return ParentNode("p", children)

def markdown_to_html_node(markdown):
    """Convert full markdown document to a single parent HTMLNode"""
    blocks = markdown_to_blocks(markdown)
    html_blocks = []
    
    for block in blocks:
        block_type = block_to_block_type(block)
        
        if block_type == BlockType.HEADING:
            html_blocks.append(heading_to_html(block))
        elif block_type == BlockType.CODE:
            html_blocks.append(code_to_html(block))
        elif block_type == BlockType.QUOTE:
            html_blocks.append(quote_to_html(block))
        elif block_type == BlockType.UNORDERED_LIST:
            html_blocks.append(unordered_list_to_html(block))
        elif block_type == BlockType.ORDERED_LIST:
            html_blocks.append(ordered_list_to_html(block))
        else:  # PARAGRAPH
            html_blocks.append(paragraph_to_html(block))
    
    return ParentNode("div", html_blocks)

def extract_title(markdown):
    """
    Extract the h1 header from markdown content.
    Raises Exception if no h1 header is found.
    """
    lines = markdown.split('\n')
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('# '):
            return stripped[2:].strip()
    
    raise Exception("No h1 header found in markdown")

