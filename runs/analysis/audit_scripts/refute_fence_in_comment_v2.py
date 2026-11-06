import sys; sys.path.insert(0, "/Users/dhaneshneelamana/projects/wsp-replication")
import wsp
cases = {
 "comment mentions ```python``` mid-line": "Design.\n```edits\nb1[0] = 1\n# same as the ```python``` snippet above\nb1[1] = 2\nb1[2] = 3\n```\n",
 "trailing comment with ``` after statement": "```edits\nb1[0] = 1   # not a ``` fence\nb1[1] = 2\n```\n",
 "control: no backticks in comment": "```edits\nb1[0] = 1\n# plain comment\nb1[1] = 2\nb1[2] = 3\n```\n",
}
for name, text in cases.items():
    net, rep = wsp.apply_edits(text)
    print(f"{name}: b1[:3]={net['b1'][:3]} statements={rep.statements} applied={rep.applied} errors={rep.errors}")
    print("   block seen by wsp:", repr(wsp.last_edits_block(text)))
try:
    import markdown_it
    md = markdown_it.MarkdownIt("commonmark")
    for name, text in cases.items():
        toks = [t for t in md.parse(text) if t.type == "fence"]
        print("CommonMark fence content:", name, repr(toks[-1].content))
except ImportError:
    print("markdown_it not installed")
