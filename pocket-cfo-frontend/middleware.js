/*
Middleware
Global gateway evaluating routing matrices protecting unauthorized dashboard incursions natively.
*/

export { default } from "next-auth/middleware";

export const config = {
  matcher: ["/dashboard/:path*"]
};
