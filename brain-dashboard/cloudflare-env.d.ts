declare namespace Cloudflare {
  interface Env {
    BRAIN_MCP_URL?: string;
    DB?: D1Database;
    BUCKET?: R2Bucket;
  }
}
