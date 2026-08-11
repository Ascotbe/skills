import type { APIRoute } from "astro";

import {
  API_CATALOG_PATH,
  apiCatalogContentType,
  buildApiCatalogDocument,
  buildDiscoveryLinkHeader,
  getSiteOrigin,
} from "../../lib/agent-discovery";

const catalogHeaders = (origin: string): HeadersInit => ({
  "Content-Type": apiCatalogContentType(),
  Link: buildDiscoveryLinkHeader(origin),
  "Cache-Control": "public, max-age=3600",
});

export const GET: APIRoute = ({ site }) => {
  const origin = getSiteOrigin(site);
  return new Response(JSON.stringify(buildApiCatalogDocument(origin), null, 2), {
    headers: catalogHeaders(origin),
  });
};

export const HEAD: APIRoute = ({ site }) => {
  const origin = getSiteOrigin(site);
  return new Response(null, {
    status: 200,
    headers: {
      ...catalogHeaders(origin),
      // RFC 9727 §2: HEAD must include the api-catalog link relation.
      Link: `<${origin}${API_CATALOG_PATH}>; rel="api-catalog"; type="application/linkset+json"`,
    },
  });
};
