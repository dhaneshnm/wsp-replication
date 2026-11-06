try:
    from markdown_it import MarkdownIt
except ImportError:
    print("markdown_it not installed"); raise SystemExit
md = MarkdownIt("commonmark")
toks = md.parse("Design\n```edits\nb1[0] = 7\nb1[1] = 8\n")
print([(t.type, t.info, t.content) for t in toks if t.type == "fence"])
