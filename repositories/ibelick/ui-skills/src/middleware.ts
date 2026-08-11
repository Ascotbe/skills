import { defineMiddleware } from "astro:middleware";

import { buildDiscoveryLinkHeader, getSiteOrigin } from "./lib/agent-discovery";
import { maybeNegotiateMarkdown } from "./lib/markdown-negotiation";

const securityHeaders = {
  "Content-Security-Policy":
    "default-src 'self'; script-src 'self' 'unsafe-inline' https://assets.onedollarstats.com; style-src 'self' 'unsafe-inline'; img-src 'self' https: data:; font-src 'self'; connect-src 'self' https://api.interfaceoffice.com https://collector.onedollarstats.com; frame-ancestors 'none'; base-uri 'self'; form-action 'self'; object-src 'none'",
  "Permissions-Policy": "camera=(), geolocation=(), microphone=()",
  "Referrer-Policy": "strict-origin-when-cross-origin",
  "X-Content-Type-Options": "nosniff",
  "X-Frame-Options": "DENY",
};

function applyResponseHeaders(
  response: Response,
  origin: string,
): Response {
  Object.entries(securityHeaders).forEach(([key, value]) =>
    response.headers.set(key, value),
  );
  // RFC 8288 discovery links for agents (isitagentready.com linkHeaders check).
  if (!response.headers.has("Link")) {
    response.headers.set("Link", buildDiscoveryLinkHeader(origin));
  }
  return response;
}

export const onRequest = defineMiddleware(async (context, next) => {
  const url = new URL(context.request.url);
  const origin = getSiteOrigin(context.site);

  if (url.pathname !== "/" && url.pathname.endsWith("/")) {
    url.pathname = url.pathname.replace(/\/+$/, "");
    const status =
      context.request.method === "GET" || context.request.method === "HEAD"
        ? 301
        : 308;
    const response = Response.redirect(url, status);
    return applyResponseHeaders(response, origin);
  }

  const response = applyResponseHeaders(await next(), origin);
  return maybeNegotiateMarkdown(context.request, response);
});
