import unittest
from block_processing import *


class TestMarkdownToBlocks(unittest.TestCase):
    def test_markdown_to_blocks(self):
        md = """
This is **bolded** paragraph

This is another paragraph with _italic_ text and `code` here
This is the same paragraph on a new line

- This is a list
- with items
"""
        blocks = markdown_to_blocks(md)
        self.assertEqual(
            blocks,
            [
                "This is **bolded** paragraph",
                "This is another paragraph with _italic_ text and `code` here\nThis is the same paragraph on a new line",
                "- This is a list\n- with items",
            ],
        )

    def test_markdown_to_blocks_single_block(self):
        md = "Just a single block of text"
        blocks = markdown_to_blocks(md)
        self.assertEqual(blocks, ["Just a single block of text"])

    def test_markdown_to_blocks_multiple_blank_lines(self):
        md = "First block\n\n\n\nSecond block\n\n\nThird block"
        blocks = markdown_to_blocks(md)
        self.assertEqual(
            blocks,
            [
                "First block",
                "Second block",
                "Third block"
            ]
        )

    def test_markdown_to_blocks_leading_trailing_whitespace(self):
        md = "   First block with spaces   \n\n  Second block with spaces  "
        blocks = markdown_to_blocks(md)
        self.assertEqual(
            blocks,
            [
                "First block with spaces",
                "Second block with spaces"
            ]
        )

    def test_markdown_to_blocks_empty_string(self):
        md = ""
        blocks = markdown_to_blocks(md)
        self.assertEqual(blocks, [])

    def test_markdown_to_blocks_only_whitespace(self):
        md = "   \n\n   \n\n   "
        blocks = markdown_to_blocks(md)
        self.assertEqual(blocks, [])

    def test_markdown_to_blocks_complex_blocks(self):
        md = """
# Heading 1

This is a paragraph with **bold** and _italic_ text.

## Heading 2

- List item 1
- List item 2
- List item 3

Another paragraph here.
"""
        blocks = markdown_to_blocks(md)
        self.assertEqual(
            blocks,
            [
                "# Heading 1",
                "This is a paragraph with **bold** and _italic_ text.",
                "## Heading 2",
                "- List item 1\n- List item 2\n- List item 3",
                "Another paragraph here."
            ]
        )

    def test_markdown_to_blocks_preserve_internal_newlines(self):
        md = "First line\nSecond line\n\nThird block"
        blocks = markdown_to_blocks(md)
        self.assertEqual(
            blocks,
            [
                "First line\nSecond line",
                "Third block"
            ]
        )

    def test_markdown_to_blocks_windows_line_endings(self):
        md = "First block\r\n\r\nSecond block"
        blocks = markdown_to_blocks(md)
        self.assertEqual(
            blocks,
            [
                "First block",
                "Second block"
            ]
        )

    def test_markdown_to_blocks_mixed_line_endings(self):
        md = "First block\n\r\nSecond block"
        blocks = markdown_to_blocks(md)
        self.assertEqual(
            blocks,
            [
                "First block",
                "Second block"
            ]
        )

class TestBlockToBlockType(unittest.TestCase):
    def test_heading(self):
        self.assertEqual(block_to_block_type("# Heading 1"), BlockType.HEADING)
        self.assertEqual(block_to_block_type("## Heading 2"), BlockType.HEADING)
        self.assertEqual(block_to_block_type("### Heading 3"), BlockType.HEADING)
        self.assertEqual(block_to_block_type("#### Heading 4"), BlockType.HEADING)
        self.assertEqual(block_to_block_type("##### Heading 5"), BlockType.HEADING)
        self.assertEqual(block_to_block_type("###### Heading 6"), BlockType.HEADING)

    def test_code_block(self):
        code_block = "```\ncode here\nmore code\n```"
        self.assertEqual(block_to_block_type(code_block), BlockType.CODE)
        
        code_block_with_lang = "```python\nprint('hello')\n```"
        self.assertEqual(block_to_block_type(code_block_with_lang), BlockType.CODE)

    def test_quote_block(self):
        quote_block = "> This is a quote\n> This is also part of the quote"
        self.assertEqual(block_to_block_type(quote_block), BlockType.QUOTE)
        
        single_line_quote = "> Single line quote"
        self.assertEqual(block_to_block_type(single_line_quote), BlockType.QUOTE)

    def test_unordered_list(self):
        ul_block = "- Item 1\n- Item 2\n- Item 3"
        self.assertEqual(block_to_block_type(ul_block), BlockType.UNORDERED_LIST)
        
        ul_with_spaces = "- Item 1\n-  Item 2"  # Note: extra space after -
        self.assertEqual(block_to_block_type(ul_with_spaces), BlockType.UNORDERED_LIST)

    def test_ordered_list(self):
        ol_block = "1. First item\n2. Second item\n3. Third item"
        self.assertEqual(block_to_block_type(ol_block), BlockType.ORDERED_LIST)
        
        ol_large = "1. Item\n2. Item\n3. Item\n4. Item\n5. Item"
        self.assertEqual(block_to_block_type(ol_large), BlockType.ORDERED_LIST)

    def test_paragraph(self):
        self.assertEqual(block_to_block_type("Just a regular paragraph"), BlockType.PARAGRAPH)
        
        multi_line_para = "This is a paragraph\nwith multiple lines\nbut no special formatting"
        self.assertEqual(block_to_block_type(multi_line_para), BlockType.PARAGRAPH)

    def test_edge_cases(self):
        # Heading without space after #
        self.assertEqual(block_to_block_type("#Heading"), BlockType.PARAGRAPH)
        
        # Too many # for heading
        self.assertEqual(block_to_block_type("####### Not a heading"), BlockType.PARAGRAPH)
        
        # Code block that doesn't end with backticks
        self.assertEqual(block_to_block_type("```code without closing"), BlockType.PARAGRAPH)
        
        # Mixed quote lines
        mixed_quote = "> Quote line\nNot a quote line"
        self.assertEqual(block_to_block_type(mixed_quote), BlockType.PARAGRAPH)
        
        # Unordered list with inconsistent formatting
        mixed_ul = "- Item 1\n* Item 2"  # * instead of -
        self.assertEqual(block_to_block_type(mixed_ul), BlockType.PARAGRAPH)
        
        # Ordered list with wrong numbering
        wrong_ol = "1. First\n3. Third"  # Missing 2.
        self.assertEqual(block_to_block_type(wrong_ol), BlockType.PARAGRAPH)
        
        # Ordered list starting from wrong number
        wrong_start_ol = "2. First\n3. Second"
        self.assertEqual(block_to_block_type(wrong_start_ol), BlockType.PARAGRAPH)

    def test_complex_blocks(self):
        # Paragraph with markdown inside
        complex_para = "This has **bold** and _italic_ but is still a paragraph"
        self.assertEqual(block_to_block_type(complex_para), BlockType.PARAGRAPH)
        
        # Heading with formatting
        formatted_heading = "## Heading with **bold** text"
        self.assertEqual(block_to_block_type(formatted_heading), BlockType.HEADING)
        
        # Code block with empty lines
        code_with_empty = "```\nline1\n\nline2\n```"
        self.assertEqual(block_to_block_type(code_with_empty), BlockType.CODE)

    def test_single_line_blocks(self):
        self.assertEqual(block_to_block_type("- single item"), BlockType.UNORDERED_LIST)
        self.assertEqual(block_to_block_type("1. single item"), BlockType.ORDERED_LIST)
        self.assertEqual(block_to_block_type("> single quote"), BlockType.QUOTE)
        self.assertEqual(block_to_block_type("```single line code```"), BlockType.CODE)

    def test_empty_blocks(self):
        # These should be filtered out by markdown_to_blocks, but test edge cases
        self.assertEqual(block_to_block_type(""), BlockType.PARAGRAPH)
        self.assertEqual(block_to_block_type("   "), BlockType.PARAGRAPH)

class TestMarkdownToHTMLNode(unittest.TestCase):
    def test_paragraphs(self):
        md = """
This is **bolded** paragraph
text in a p
tag here

This is another paragraph with _italic_ text and `code` here

"""
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><p>This is <b>bolded</b> paragraph text in a p tag here</p><p>This is another paragraph with <i>italic</i> text and <code>code</code> here</p></div>",
        )

    def test_codeblock(self):
        md = """
```\nThis is text that _should_ remain\nthe **same** even with inline stuff\n```
"""
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><pre><code>This is text that _should_ remain\nthe **same** even with inline stuff\n</code></pre></div>",
        )

    def test_headings(self):
        md = """
# Heading 1

## Heading 2 with **bold**

### Heading 3
"""
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><h1>Heading 1</h1><h2>Heading 2 with <b>bold</b></h2><h3>Heading 3</h3></div>",
        )

    def test_quote(self):
        md = """
> This is a quote
> with multiple lines
> and **bold** text
"""
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><blockquote>This is a quote with multiple lines and <b>bold</b> text</blockquote></div>",
        )

    def test_unordered_list(self):
        md = """
- Item 1 with **bold**
- Item 2 with _italic_
- Item 3 with `code`
"""
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><ul><li>Item 1 with <b>bold</b></li><li>Item 2 with <i>italic</i></li><li>Item 3 with <code>code</code></li></ul></div>",
        )

    def test_ordered_list(self):
        md = """
1. First item with **bold**
2. Second item with _italic_
3. Third item with `code`
"""
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><ol><li>First item with <b>bold</b></li><li>Second item with <i>italic</i></li><li>Third item with <code>code</code></li></ol></div>",
        )

    def test_mixed_blocks():
        md = """# Main Heading

This is a paragraph with **bold** text.

- List item 1
- List item 2

> A wise quote here

```
print("hello world")
```

text
"""
    
        node = markdown_to_html_node(md)
        html = node.to_html()
        # just verify it contains the expected elements
        self.assertin("<h1>main heading</h1>", html)
        self.assertin("<p>this is a paragraph with <strong>bold</strong> text.</p>", html)
        self.assertin("<ul><li>list item 1</li><li>list item 2</li></ul>", html)
        self.assertin("<blockquote>a wise quote here</blockquote>", html)
        self.assertIn("<pre><code>print(\"hello world\")\n</code></pre>", html)

    def test_empty_markdown(self):
        md = ""
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(html, "<div></div>")

    def test_single_paragraph(self):
        md = "Just a single paragraph"
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(html, "<div><p>Just a single paragraph</p></div>")

def test_extract_title():
    # Test normal case
    markdown = "# My Title\nSome content"
    assert extract_title(markdown) == "My Title"
    
    # Test with whitespace
    markdown = "  #  My Title  \nSome content"
    assert extract_title(markdown) == "My Title"
    
    # Test no h1 header
    try:
        extract_title("## Not H1\nSome content")
        assert False, "Should have raised exception"
    except Exception as e:
        assert str(e) == "No h1 header found in markdown"
    
    # Test multiple headers - should take first h1
    markdown = "# First Title\n# Second Title"
    assert extract_title(markdown) == "First Title"

if __name__ == "__main__":
    unittest.main()
