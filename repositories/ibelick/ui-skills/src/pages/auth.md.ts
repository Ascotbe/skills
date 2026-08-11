import type { APIRoute } from "astro";

import {
  buildAuthMarkdown,
  getSiteOrigin,
  markdownHeaders,
} from "../lib/oauth-discovery";

export const GET: APIRoute = ({ site }) => {
  const origin = getSiteOrigin(site);
  return new Response(buildAuthMarkdown(origin), {
    headers: markdownHeaders,
  });
};

export const HEAD: APIRoute = () =>
  new Response(null, { status: 200, headers: markdownHeaders });
