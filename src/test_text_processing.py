import unittest
from textnode import TextNode, TextType
from text_processing import (
    split_nodes_delimiter, 
    extract_markdown_images, 
    extract_markdown_links, 
    split_nodes_image, 
    split_nodes_link, 
    text_to_textnodes  # Add this import
)
# ... keep all existing TestSplitNodesDelimiter and TestExtractMarkdown tests ...

class TestSplitNodesImage(unittest.TestCase):
    def test_split_images(self):
        node = TextNode(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png) and another ![second image](https://i.imgur.com/3elNhQu.png)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("This is text with an ", TextType.TEXT),
                TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
                TextNode(" and another ", TextType.TEXT),
                TextNode(
                    "second image", TextType.IMAGE, "https://i.imgur.com/3elNhQu.png"
                ),
            ],
            new_nodes,
        )

    def test_split_single_image(self):
        node = TextNode(
            "Text before ![alt text](image.png) text after",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image([node])
        expected = [
            TextNode("Text before ", TextType.TEXT),
            TextNode("alt text", TextType.IMAGE, "image.png"),
            TextNode(" text after", TextType.TEXT),
        ]
        self.assertListEqual(expected, new_nodes)

    def test_split_image_at_start(self):
        node = TextNode(
            "![alt text](image.png) text after",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image([node])
        expected = [
            TextNode("alt text", TextType.IMAGE, "image.png"),
            TextNode(" text after", TextType.TEXT),
        ]
        self.assertListEqual(expected, new_nodes)

    def test_split_image_at_end(self):
        node = TextNode(
            "Text before ![alt text](image.png)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image([node])
        expected = [
            TextNode("Text before ", TextType.TEXT),
            TextNode("alt text", TextType.IMAGE, "image.png"),
        ]
        self.assertListEqual(expected, new_nodes)

    def test_split_only_image(self):
        node = TextNode(
            "![alt text](image.png)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image([node])
        expected = [
            TextNode("alt text", TextType.IMAGE, "image.png"),
        ]
        self.assertListEqual(expected, new_nodes)

    def test_no_images(self):
        node = TextNode(
            "This is just plain text with no images",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image([node])
        expected = [TextNode("This is just plain text with no images", TextType.TEXT)]
        self.assertListEqual(expected, new_nodes)

    def test_non_text_nodes_untouched(self):
        nodes = [
            TextNode("This is text", TextType.TEXT),
            TextNode("This is bold", TextType.BOLD),
            TextNode("Text with ![image](img.png)", TextType.TEXT),
        ]
        new_nodes = split_nodes_image(nodes)
        expected = [
            TextNode("This is text", TextType.TEXT),
            TextNode("This is bold", TextType.BOLD),
            TextNode("Text with ", TextType.TEXT),
            TextNode("image", TextType.IMAGE, "img.png"),
        ]
        self.assertListEqual(expected, new_nodes)

    def test_empty_alt_text(self):
        node = TextNode(
            "Text before ![](image.png) text after",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image([node])
        expected = [
            TextNode("Text before ", TextType.TEXT),
            TextNode("", TextType.IMAGE, "image.png"),
            TextNode(" text after", TextType.TEXT),
        ]
        self.assertListEqual(expected, new_nodes)


class TestSplitNodesLink(unittest.TestCase):
    def test_split_links(self):
        node = TextNode(
            "This is text with a [link](https://www.boot.dev) and another [second link](https://www.google.com)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_link([node])
        self.assertListEqual(
            [
                TextNode("This is text with a ", TextType.TEXT),
                TextNode("link", TextType.LINK, "https://www.boot.dev"),
                TextNode(" and another ", TextType.TEXT),
                TextNode(
                    "second link", TextType.LINK, "https://www.google.com"
                ),
            ],
            new_nodes,
        )

    def test_split_single_link(self):
        node = TextNode(
            "Text before [anchor text](https://example.com) text after",
            TextType.TEXT,
        )
        new_nodes = split_nodes_link([node])
        expected = [
            TextNode("Text before ", TextType.TEXT),
            TextNode("anchor text", TextType.LINK, "https://example.com"),
            TextNode(" text after", TextType.TEXT),
        ]
        self.assertListEqual(expected, new_nodes)

    def test_split_link_at_start(self):
        node = TextNode(
            "[anchor text](https://example.com) text after",
            TextType.TEXT,
        )
        new_nodes = split_nodes_link([node])
        expected = [
            TextNode("anchor text", TextType.LINK, "https://example.com"),
            TextNode(" text after", TextType.TEXT),
        ]
        self.assertListEqual(expected, new_nodes)

    def test_split_link_at_end(self):
        node = TextNode(
            "Text before [anchor text](https://example.com)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_link([node])
        expected = [
            TextNode("Text before ", TextType.TEXT),
            TextNode("anchor text", TextType.LINK, "https://example.com"),
        ]
        self.assertListEqual(expected, new_nodes)

    def test_split_only_link(self):
        node = TextNode(
            "[anchor text](https://example.com)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_link([node])
        expected = [
            TextNode("anchor text", TextType.LINK, "https://example.com"),
        ]
        self.assertListEqual(expected, new_nodes)

    def test_no_links(self):
        node = TextNode(
            "This is just plain text with no links",
            TextType.TEXT,
        )
        new_nodes = split_nodes_link([node])
        expected = [TextNode("This is just plain text with no links", TextType.TEXT)]
        self.assertListEqual(expected, new_nodes)

    def test_non_text_nodes_untouched_links(self):
        nodes = [
            TextNode("This is text", TextType.TEXT),
            TextNode("This is italic", TextType.ITALIC),
            TextNode("Text with [link](site.com)", TextType.TEXT),
        ]
        new_nodes = split_nodes_link(nodes)
        expected = [
            TextNode("This is text", TextType.TEXT),
            TextNode("This is italic", TextType.ITALIC),
            TextNode("Text with ", TextType.TEXT),
            TextNode("link", TextType.LINK, "site.com"),
        ]
        self.assertListEqual(expected, new_nodes)

    def test_empty_anchor_text(self):
        node = TextNode(
            "Text before [](https://example.com) text after",
            TextType.TEXT,
        )
        new_nodes = split_nodes_link([node])
        expected = [
            TextNode("Text before ", TextType.TEXT),
            TextNode("", TextType.LINK, "https://example.com"),
            TextNode(" text after", TextType.TEXT),
        ]
        self.assertListEqual(expected, new_nodes)

    def test_mixed_images_and_links(self):
        # Note: This tests that each function only handles its respective type
        node = TextNode(
            "Text with ![image](img.png) and [link](site.com)",
            TextType.TEXT,
        )
        image_nodes = split_nodes_image([node])
        link_nodes = split_nodes_link(image_nodes)
        
        # After splitting images, then links
        expected = [
            TextNode("Text with ", TextType.TEXT),
            TextNode("image", TextType.IMAGE, "img.png"),
            TextNode(" and ", TextType.TEXT),
            TextNode("link", TextType.LINK, "site.com"),
        ]
        self.assertListEqual(expected, link_nodes)


class TestTextToTextNodes(unittest.TestCase):
    def test_text_to_textnodes_complex(self):
        text = "This is **text** with an _italic_ word and a `code block` and an ![obi wan image](https://i.imgur.com/fJRm4Vk.jpeg) and a [link](https://boot.dev)"
        nodes = text_to_textnodes(text)
        expected = [
            TextNode("This is ", TextType.TEXT),
            TextNode("text", TextType.BOLD),
            TextNode(" with an ", TextType.TEXT),
            TextNode("italic", TextType.ITALIC),
            TextNode(" word and a ", TextType.TEXT),
            TextNode("code block", TextType.CODE),
            TextNode(" and an ", TextType.TEXT),
            TextNode("obi wan image", TextType.IMAGE, "https://i.imgur.com/fJRm4Vk.jpeg"),
            TextNode(" and a ", TextType.TEXT),
            TextNode("link", TextType.LINK, "https://boot.dev"),
        ]
        self.assertListEqual(expected, nodes)

    def test_text_to_textnodes_simple(self):
        text = "Just plain text"
        nodes = text_to_textnodes(text)
        expected = [TextNode("Just plain text", TextType.TEXT)]
        self.assertListEqual(expected, nodes)

    def test_text_to_textnodes_bold_only(self):
        text = "This is **bold** text"
        nodes = text_to_textnodes(text)
        expected = [
            TextNode("This is ", TextType.TEXT),
            TextNode("bold", TextType.BOLD),
            TextNode(" text", TextType.TEXT),
        ]
        self.assertListEqual(expected, nodes)

    def test_text_to_textnodes_italic_only(self):
        text = "This is _italic_ text"
        nodes = text_to_textnodes(text)
        expected = [
            TextNode("This is ", TextType.TEXT),
            TextNode("italic", TextType.ITALIC),
            TextNode(" text", TextType.TEXT),
        ]
        self.assertListEqual(expected, nodes)

    def test_text_to_textnodes_code_only(self):
        text = "This is `code` text"
        nodes = text_to_textnodes(text)
        expected = [
            TextNode("This is ", TextType.TEXT),
            TextNode("code", TextType.CODE),
            TextNode(" text", TextType.TEXT),
        ]
        self.assertListEqual(expected, nodes)

    def test_text_to_textnodes_image_only(self):
        text = "This is an ![image](image.png)"
        nodes = text_to_textnodes(text)
        expected = [
            TextNode("This is an ", TextType.TEXT),
            TextNode("image", TextType.IMAGE, "image.png"),
        ]
        self.assertListEqual(expected, nodes)

    def test_text_to_textnodes_link_only(self):
        text = "This is a [link](https://example.com)"
        nodes = text_to_textnodes(text)
        expected = [
            TextNode("This is a ", TextType.TEXT),
            TextNode("link", TextType.LINK, "https://example.com"),
        ]
        self.assertListEqual(expected, nodes)

    def test_text_to_textnodes_multiple_formats(self):
        text = "**Bold** and _italic_ and `code`"
        nodes = text_to_textnodes(text)
        expected = [
            TextNode("Bold", TextType.BOLD),
            TextNode(" and ", TextType.TEXT),
            TextNode("italic", TextType.ITALIC),
            TextNode(" and ", TextType.TEXT),
            TextNode("code", TextType.CODE),
        ]
        self.assertListEqual(expected, nodes)

    def test_text_to_textnodes_mixed_images_links(self):
        text = "See this ![image](img.png) and this [link](site.com)"
        nodes = text_to_textnodes(text)
        expected = [
            TextNode("See this ", TextType.TEXT),
            TextNode("image", TextType.IMAGE, "img.png"),
            TextNode(" and this ", TextType.TEXT),
            TextNode("link", TextType.LINK, "site.com"),
        ]
        self.assertListEqual(expected, nodes)

    def test_text_to_textnodes_formatting_within_text(self):
        text = "Start with **bold** then _italic_ then `code` then normal text"
        nodes = text_to_textnodes(text)
        expected = [
            TextNode("Start with ", TextType.TEXT),
            TextNode("bold", TextType.BOLD),
            TextNode(" then ", TextType.TEXT),
            TextNode("italic", TextType.ITALIC),
            TextNode(" then ", TextType.TEXT),
            TextNode("code", TextType.CODE),
            TextNode(" then normal text", TextType.TEXT),
        ]
        self.assertListEqual(expected, nodes)

    def test_text_to_textnodes_empty_text(self):
        text = ""
        nodes = text_to_textnodes(text)
        expected = [TextNode("", TextType.TEXT)]
        self.assertListEqual(expected, nodes)

def test_text_to_textnodes_only_delimiters(self):
        text = "****"
        nodes = text_to_textnodes(text)
        # With "****", we split by "**" into ["", "", ""]
        # We skip empty parts but the middle empty part becomes bold
        # So we get one bold node with empty text
        expected = [TextNode("", TextType.BOLD)]
        self.assertListEqual(expected, nodes)

def test_text_to_textnodes_complex_nested_lookalike(self):
        # Test that images are processed before links (so ![text](url) doesn't get mistaken for a link)
        text = "This has ![image](img.png) and [link](site.com) and also **bold** text"
        nodes = text_to_textnodes(text)
        expected = [
            TextNode("This has ", TextType.TEXT),
            TextNode("image", TextType.IMAGE, "img.png"),
            TextNode(" and ", TextType.TEXT),
            TextNode("link", TextType.LINK, "site.com"),
            TextNode(" and also ", TextType.TEXT),
            TextNode("bold", TextType.BOLD),
            TextNode(" text", TextType.TEXT),
        ]
        self.assertListEqual(expected, nodes)

if __name__ == "__main__":
    unittest.main()
