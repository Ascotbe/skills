import type { APIRoute } from "astro";
import designDocument from "../../DESIGN.md?raw";

export const GET: APIRoute = () =>
  new Response(designDocument, {
    headers: {
      "Content-Type": "text/markdown; charset=utf-8",
    },
  });
