import { QuartzComponent, QuartzComponentConstructor } from "./types"

interface Options {
  condition?: "index" | "not-index" | "all"
}

const CoverImage: QuartzComponent = ({ fileData, cfg, displayClass }) => {
  const fm = fileData.frontmatter as Record<string, any> | undefined
  const cover = fm?.cover_image || fm?.image_url || fm?.thumbnail

  if (!cover) return null

  // Skip jika di homepage dan condition = not-index
  const isIndex = fileData.slug === "index" || fileData.slug === "404"
  if (displayClass === "not-index" && isIndex) return null
  if ((displayClass as string) === "index" && !isIndex) return null

  return (
    <div class={`cover-image ${displayClass ?? ""}`}>
      <img src={cover} alt={fm?.title ?? ""} loading="lazy" />
    </div>
  )
}

CoverImage.displayName = "CoverImage"
CoverImage.css = `
.cover-image {
  margin-bottom: 2rem;
  overflow: hidden;
  border-radius: 8px;
}
.cover-image img {
  width: 100%;
  height: auto;
  display: block;
  object-fit: cover;
  max-height: 400px;
}
`

export default ((opts?: Options) => {
  const condition = opts?.condition ?? "all"
  if (condition === "not-index") {
    CoverImage.displayClass = "not-index"
  }
  return CoverImage
}) satisfies QuartzComponentConstructor
