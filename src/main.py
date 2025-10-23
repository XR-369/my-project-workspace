from textnode import TextNode, TextType
import os
import shutil
import sys
from block_processing import markdown_to_html_node, extract_title
from pathlib import Path


def copy_directory_contents(src_dir, dest_dir):
    """
    Recursively copy all contents from src_dir to dest_dir.
    First deletes the destination directory if it exists.
    """
    # Remove destination directory if it exists
    if os.path.exists(dest_dir):
        print(f"Removing existing directory: {dest_dir}")
        shutil.rmtree(dest_dir)
    
    # Create destination directory
    print(f"Creating directory: {dest_dir}")
    os.makedirs(dest_dir)
    
    # Copy all files and subdirectories recursively
    copy_recursive(src_dir, dest_dir)

def copy_recursive(src, dest):
    """
    Recursive helper function to copy files and directories
    """
    # Ensure destination directory exists
    if not os.path.exists(dest):
        os.makedirs(dest)
    
    # Iterate through all items in source directory
    for item in os.listdir(src):
        src_path = os.path.join(src, item)
        dest_path = os.path.join(dest, item)
        
        if os.path.isfile(src_path):
            # Copy file
            shutil.copy(src_path, dest_path)
            print(f"Copied file: {src_path} -> {dest_path}")
        else:
            # Recursively copy directory
            print(f"Copying directory: {src_path} -> {dest_path}")
            copy_recursive(src_path, dest_path)

def main():
    # Get basepath from CLI args or default to "/"
    basepath = sys.argv[1] if len(sys.argv) > 1 else "/"
    print(f"Using basepath: {basepath}")
    
    # Copy static files to docs directory (for GitHub Pages)
    print("Starting static file copy...")
    copy_directory_contents("static", "docs")
    print("Static files copied successfully!")

    # Generate all pages recursively with basepath
    generate_pages_recursive("content", "template.html", "docs", basepath)
    
    print("All pages generated successfully!")

def generate_page(from_path, template_path, dest_path, basepath="/"):
    """
    Generate an HTML page from markdown using a template with basepath support.
    """
    print(f"Generating page from {from_path} to {dest_path} using {template_path}")
    
    # Read markdown file
    with open(from_path, 'r') as f:
        markdown = f.read()
    
    # Read template file
    with open(template_path, 'r') as f:
        template = f.read()
    
    # Convert markdown to HTML
    html_node = markdown_to_html_node(markdown)
    content = html_node.to_html()
    
    # Extract title
    title = extract_title(markdown)
    
    # Replace placeholders in template
    html_output = template.replace('{{ Title }}', title).replace('{{ Content }}', content)
    
    # Replace absolute paths with basepath
    html_output = html_output.replace('href="/', f'href="{basepath}')
    html_output = html_output.replace('src="/', f'src="{basepath}')
    
    # Ensure destination directory exists
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    
    # Write HTML file
    with open(dest_path, 'w') as f:
        f.write(html_output)

def generate_pages_recursive(dir_path_content, template_path, dest_dir_path, basepath="/"):
    """
    Recursively generate HTML pages from all markdown files in content directory.
    """
    content_path = Path(dir_path_content)
    dest_path = Path(dest_dir_path)
    
    # Ensure destination directory exists
    dest_path.mkdir(parents=True, exist_ok=True)
    
    # Iterate through all items recursively
    for item in content_path.rglob('*'):
        if item.is_file() and item.suffix == '.md':
            # Calculate relative path from content directory
            relative_path = item.relative_to(content_path)
            # Change .md to .html and build destination path
            html_filename = relative_path.with_suffix('.html')
            html_dest_path = dest_path / html_filename
            
            # Ensure parent directory exists
            html_dest_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Generate the page with basepath
            generate_page(str(item), template_path, str(html_dest_path), basepath)


if __name__ == "__main__":
    main()

