import { Helmet } from "react-helmet-async";

type SeoProps = {
  title: string;
  description: string;
  path: string;
  index?: boolean;
  jsonLd?: Record<string, unknown>;
};

export function Seo({ title, description, path, index = true, jsonLd }: SeoProps) {
  const origin = typeof window === "undefined" ? "http://localhost:5173" : window.location.origin;
  const canonical = `${origin}${path}`;
  return (
    <Helmet>
      <title>{title}</title>
      <meta name="description" content={description} />
      <link rel="canonical" href={canonical} />
      <meta property="og:title" content={title} />
      <meta property="og:description" content={description} />
      <meta property="og:type" content="website" />
      <meta property="og:url" content={canonical} />
      <meta name="robots" content={index ? "index, follow" : "noindex, nofollow"} />
      {jsonLd ? <script type="application/ld+json">{JSON.stringify(jsonLd)}</script> : null}
    </Helmet>
  );
}
