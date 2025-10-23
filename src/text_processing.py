import re
from textnode import TextNode, TextType

def extract_markdown_images(text):
    """Extract markdown images from text and return list of (alt_text, url) tuples"""
    pattern = r"!\[([^\[\]]*)\]\(([^\(\)]*)\)"
    matches = re.findall(pattern, text)
    return matches

def extract_markdown_links(text):
    """Extract markdown links from text and return list of (anchor_text, url) tuples"""
    pattern = r"(?<!!)\[([^\[\]]*)\]\(([^\(\)]*)\)"
    matches = re.findall(pattern, text)
    return matches

def split_nodes_delimiter(old_nodes, delimiter, text_type):
    new_nodes = []
    
    for node in old_nodes:
        # If it's not a text node, add it as-is and continue
        if node.text_type != TextType.TEXT:
            new_nodes.append(node)
            continue
        
        text = node.text
        split_parts = text.split(delimiter)
        
        # If there's an odd number of parts, it means unmatched delimiters
        if len(split_parts) % 2 == 0:
            raise ValueError(f"Invalid markdown: unmatched delimiter '{delimiter}' in text: {text}")
        
        # If no actual splitting occurred (no delimiters found), just add the original node
        if len(split_parts) == 1:
            new_nodes.append(node)
            continue
            
        # Process the split parts
        split_nodes = []
        for i, part in enumerate(split_parts):
            if part == "":  # Skip empty parts
                continue
            if i % 2 == 0:
                # Even indices are regular text
                split_nodes.append(TextNode(part, TextType.TEXT))
            else:
                # Odd indices are the delimited content
                split_nodes.append(TextNode(part, text_type))
        
        # Use extend to add all the split nodes to new_nodes
        new_nodes.extend(split_nodes)
    
    return new_nodes

def split_nodes_image(old_nodes):
    new_nodes = []
    
    for node in old_nodes:
        # If it's not a text node, add it as-is and continue
        if node.text_type != TextType.TEXT:
            new_nodes.append(node)
            continue
            
        text = node.text
        images = extract_markdown_images(text)
        
        # If no images found, add the original node and continue
        if not images:
            new_nodes.append(node)
            continue
            
        current_text = text
        for alt_text, url in images:
            # Split the text at the first occurrence of the image markdown
            sections = current_text.split(f"![{alt_text}]({url})", 1)
            
            # If there's text before the image, add it as a text node
            if sections[0]:
                new_nodes.append(TextNode(sections[0], TextType.TEXT))
            
            # Add the image node
            new_nodes.append(TextNode(alt_text, TextType.IMAGE, url))
            
            # Update current_text to be the remaining text after the image
            current_text = sections[1] if len(sections) > 1 else ""
        
        # Add any remaining text after the last image
        if current_text:
            new_nodes.append(TextNode(current_text, TextType.TEXT))
    
    return new_nodes

def split_nodes_link(old_nodes):
    new_nodes = []
    
    for node in old_nodes:
        # If it's not a text node, add it as-is and continue
        if node.text_type != TextType.TEXT:
            new_nodes.append(node)
            continue
            
        text = node.text
        links = extract_markdown_links(text)
        
        # If no links found, add the original node and continue
        if not links:
            new_nodes.append(node)
            continue
            
        current_text = text
        for anchor_text, url in links:
            # Split the text at the first occurrence of the link markdown
            sections = current_text.split(f"[{anchor_text}]({url})", 1)
            
            # If there's text before the link, add it as a text node
            if sections[0]:
                new_nodes.append(TextNode(sections[0], TextType.TEXT))
            
            # Add the link node
            new_nodes.append(TextNode(anchor_text, TextType.LINK, url))
            
            # Update current_text to be the remaining text after the link
            current_text = sections[1] if len(sections) > 1 else ""
        
        # Add any remaining text after the last link
        if current_text:
            new_nodes.append(TextNode(current_text, TextType.TEXT))
    
    return new_nodes

def text_to_textnodes(text):
    """Convert raw markdown text to a list of TextNodes by applying all splitting functions in order"""
    # Start with a single text node
    nodes = [TextNode(text, TextType.TEXT)]
    
    # Apply splitting functions in order of precedence
    # Images first (since they have ! prefix and shouldn't be confused with links)
    nodes = split_nodes_image(nodes)
    
    # Links second
    nodes = split_nodes_link(nodes)
    
    # Then inline formatting in order of common markdown precedence
    nodes = split_nodes_delimiter(nodes, "**", TextType.BOLD)
    nodes = split_nodes_delimiter(nodes, "_", TextType.ITALIC)  # Changed from "*" to "_"
    nodes = split_nodes_delimiter(nodes, "`", TextType.CODE)
    
    return nodes
