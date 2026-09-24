import { QuartzComponent, QuartzComponentConstructor, QuartzComponentProps } from "./types"

const Relations: QuartzComponent = ({ fileData }: QuartzComponentProps) => {
  const fm = fileData.frontmatter
  if (!fm) return null

  const relationFields: { key: string; label: string; slug: string }[] = [
    { key: "member_of", label: "Anggota dari", slug: "member_of" },
    { key: "leader_of", label: "Pemimpin dari", slug: "leader_of" },
    { key: "owner_of", label: "Pemilik dari", slug: "owner_of" },
    { key: "related", label: "Terkait dengan", slug: "related" },
  ]

  const sections = relationFields
    .map(({ key, label }) => {
      const value = fm[key]
      if (!value) return null
      const items = Array.isArray(value) ? value : [value]
      return { label, items }
    })
    .filter((s): s is { label: string; items: string[] } => s !== null && s.items.length > 0)

  if (sections.length === 0) return null

  return (
    <div className="relations-section" style={{ marginTop: "2rem", paddingTop: "1rem", borderTop: "1px solid var(--lightgray)" }}>
      <h3 style={{ marginBottom: "0.5rem" }}>Relasi</h3>
      <div style={{ display: "flex", flexDirection: "column", gap: "0.5rem" }}>
        {sections.map(({ label, items }) => (
          <div key={label} style={{ display: "flex", gap: "0.5rem", alignItems: "baseline" }}>
            <span style={{ fontWeight: 500, minWidth: "120px", fontSize: "0.9rem", color: "var(--darkgray)" }}>{label}:</span>
            <span style={{ fontSize: "0.9rem" }}>
              {items.map((item, i) => (
                <span key={item}>
                  {i > 0 && ", "}
                  <a href={`/${item}`} className="internal" style={{ color: "var(--secondary)" }}>
                    {item.replace(/-/g, " ").replace(/\b\w/g, (c) => c.toUpperCase())}
                  </a>
                </span>
              ))}
            </span>
          </div>
        ))}
      </div>
    </div>
  )
}

Relations.css = `
  .relations-section {
    background: var(--lightgray);
    padding: 1rem;
    border-radius: 4px;
  }
  .relations-section h3 {
    margin-top: 0;
  }
`

export default (() => Relations) satisfies QuartzComponentConstructor
