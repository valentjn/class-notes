-- from https://tex.stackexchange.com/a/417883
function alwaysHyphenate(head, tail)
  local n = head

  while n do
    if node.type(n.id) == 'glyph' and n.char == string.byte('-') then
      -- insert an infinite penalty before, and a zero-width glue node after, the hyphen;
      -- like writing "\nobreak-\hspace{0pt}" or equivalently "\penalty10000-\hskip0pt"
      local p = node.new(node.id('penalty'))
      p.penalty = 10000
      head, p = node.insert_before(head, n, p)
      local g = node.new(node.id('glue'))
      head, g = node.insert_after(head, n, g)
      n = g
    end

    n = n.next
  end

  lang.hyphenate(head, tail)
end

luatexbase.add_to_callback('hyphenate', alwaysHyphenate, 'Hyphenate words that contain hyphens')
