import { i18n } from "../i18n"
import { FullSlug, joinSegments, pathToRoot } from "../util/path"
import { CSSResourceToStyleElement, JSResourceToScriptElement } from "../util/resources"
import { googleFontHref, googleFontSubsetHref } from "../util/theme"
import { QuartzComponent, QuartzComponentConstructor, QuartzComponentProps } from "./types"
import { unescapeHTML } from "../util/escape"

export default (() => {
  const Head: QuartzComponent = ({
    cfg,
    fileData,
    externalResources,
    ctx,
  }: QuartzComponentProps) => {
    const titleSuffix = cfg.pageTitleSuffix ?? ""
    const title =
      (fileData.frontmatter?.title ?? i18n(cfg.locale).propertyDefaults.title) + titleSuffix
    const description =
      fileData.frontmatter?.socialDescription ??
      fileData.frontmatter?.description ??
      unescapeHTML(fileData.description?.trim() ?? i18n(cfg.locale).propertyDefaults.description)
    
    // Generate Schema.org JSON-LD
    const tags = fileData.frontmatter?.tags || []
    const date = fileData.frontmatter?.date || ""
    const baseUrl = `https://${cfg.baseUrl}`
    const pageUrl = `${baseUrl}/${fileData.slug}`
    
    const personTags = ['tokoh', 'aktor', 'politikus', 'pengusaha', 'menteri', 'presiden', 'gubernur']
    const orgTags = ['partai', 'organisasi', 'perusahaan', 'bumn', 'yayasan']
    const isPerson = tags.some((t: string) => personTags.includes(t.toLowerCase()))
    const isOrg = tags.some((t: string) => orgTags.includes(t.toLowerCase()))
    
    let mainSchema: Record<string, any> = {}
    
    if (isPerson) {
      mainSchema = {
        "@context": "https://schema.org",
        "@type": "Person",
        "name": title,
        "url": pageUrl,
        "description": description,
        "sameAs": [
          `https://id.wikipedia.org/wiki/${(fileData.slug || '').replace(/-/g, '_')}`
        ]
      }
    } else if (isOrg) {
      mainSchema = {
        "@context": "https://schema.org",
        "@type": "Organization",
        "name": title,
        "url": pageUrl,
        "description": description,
        "sameAs": [
          `https://id.wikipedia.org/wiki/${(fileData.slug || '').replace(/-/g, '_')}`
        ]
      }
    } else {
      mainSchema = {
        "@context": "https://schema.org",
        "@type": "NewsArticle",
        "headline": title,
        "url": pageUrl,
        "datePublished": date,
        "author": {
          "@type": "Person",
          "name": "Ira Amalia"
        },
        "publisher": {
          "@type": "Organization",
          "name": cfg.pageTitle,
          "logo": {
            "@type": "ImageObject",
            "url": `${baseUrl}/static/covers/ira-amalia-cover.jpg`
          }
        }
      }
    }
    
    const breadcrumbSchema = {
      "@context": "https://schema.org",
      "@type": "BreadcrumbList",
      "itemListElement": [
        {
          "@type": "ListItem",
          "position": 1,
          "name": "Home",
          "item": baseUrl
        },
        {
          "@type": "ListItem",
          "position": 2,
          "name": title,
          "item": pageUrl
        }
      ]
    }
    
    const jsonLdSchemas = JSON.stringify([mainSchema, breadcrumbSchema])

    const { css, js, additionalHead } = externalResources

    const url = new URL(`https://${cfg.baseUrl ?? "example.com"}`)
    const path = url.pathname as FullSlug
    const baseDir = fileData.slug === "404" ? path : pathToRoot(fileData.slug!)
    const iconPath = joinSegments(baseDir, "static/icon.png")

    // Url of current page
    const socialUrl =
      fileData.slug === "404" ? url.toString() : joinSegments(url.toString(), fileData.slug!)

    const usesCustomOgImage = ctx.cfg.plugins.emitters.some((e) => e.name === "CustomOgImages")
    const ogImageDefaultPath = `https://${cfg.baseUrl}/static/covers/ira-amalia-cover.jpg?v=1789776273`

    const coreStylesheet = css[0]?.content
    const coreScript = js.find(
      (r) => r.loadTime === "beforeDOMReady" && r.contentType === "external",
    )

    return (
      <head>
        <title>{title}</title>
        <meta charSet="utf-8" />
        {coreStylesheet && <link rel="preload" href={coreStylesheet} as="style" />}
        {coreScript && coreScript.contentType === "external" && (
          <link rel="preload" href={coreScript.src} as="script" />
        )}
        {cfg.theme.cdnCaching && cfg.theme.fontOrigin === "googleFonts" && (
          <>
            <link rel="preconnect" href="https://fonts.googleapis.com" />
            <link rel="preconnect" href="https://fonts.gstatic.com" />
            <link rel="stylesheet" href={googleFontHref(cfg.theme)} />
            {cfg.theme.typography.title && (
              <link rel="stylesheet" href={googleFontSubsetHref(cfg.theme, cfg.pageTitle)} />
            )}
          </>
        )}
        <link rel="preconnect" href="https://cdnjs.cloudflare.com" crossOrigin="anonymous" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />

        <meta name="og:site_name" content={cfg.pageTitle}></meta>
        <meta property="og:title" content={title} />
        <meta property="og:type" content="website" />
        <meta name="twitter:card" content="summary_large_image" />
        <meta name="twitter:title" content={title} />
        <meta name="twitter:description" content={description} />
        <meta property="og:description" content={description} />
        <meta property="og:image:alt" content={description} />

        {!usesCustomOgImage && (
          <>
            <meta property="og:image" content={ogImageDefaultPath} />
            <meta property="og:image:url" content={ogImageDefaultPath} />
            <meta name="twitter:image" content={ogImageDefaultPath} />
            <meta
              property="og:image:type"
              content="image/jpeg"
            />
            <meta property="og:image:width" content="2192" />
            <meta property="og:image:height" content="1152" />
            <meta property="og:logo" content={`https://${cfg.baseUrl}/static/covers/ira-amalia-cover.jpg?v=1789776273`} />
          </>
        )}

        {cfg.baseUrl && (
          <>
            <meta property="twitter:domain" content={cfg.baseUrl}></meta>
            <meta property="og:url" content={socialUrl}></meta>
            <meta property="twitter:url" content={socialUrl}></meta>
          </>
        )}

        <link rel="icon" href={iconPath} />
        <meta name="description" content={description} />
        <meta name="generator" content="Quartz" />

        {css.map((resource) => CSSResourceToStyleElement(resource, true))}
        {js
          .filter((resource) => resource.loadTime === "beforeDOMReady")
          .map((res) => JSResourceToScriptElement(res, true))}
        {additionalHead.map((resource) => {
          if (typeof resource === "function") {
            return resource(fileData)
          } else {
            return resource
          }
        })}
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: jsonLdSchemas }}
        />
      </head>
    )
  }

  return Head
}) satisfies QuartzComponentConstructor
