import { NextResponse } from 'next/server'

export function middleware(request) {
  const url = request.nextUrl

  // Restrict access to /restricted/* 
  if (url.pathname.startsWith("/restricted")) {
    return new NextResponse("Access denied", { status: 403 })
  }
  
  return NextResponse.next()
}

export const config = {
  matcher: ['/restricted/:path*'],
}