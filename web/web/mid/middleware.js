import { NextResponse } from 'next/server'

export function middleware(request) {
  const url = request.nextUrl

  // Restrict access to /restricted/* and the api thats restricted that holds the database
  if (url.pathname.startsWith("/restricted") || url.pathname.startsWith("/api/restricted")) {
    return new NextResponse("Access denied", { status: 403 })
  }
  
  return NextResponse.next()
}

export const config = {
  matcher: ['/restricted/:path*', '/api/restricted/:path*'],
}