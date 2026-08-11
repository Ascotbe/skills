import type { APIRoute } from "astro";

import { buildJwks, jsonHeaders } from "../../lib/oauth-discovery";

export const GET: APIRoute = () =>
  new Response(JSON.stringify(buildJwks(), null, 2), {
    headers: jsonHeaders,
  });

export const HEAD: APIRoute = () =>
  new Response(null, { status: 200, headers: jsonHeaders });
