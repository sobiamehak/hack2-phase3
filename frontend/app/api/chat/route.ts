import { NextRequest } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { message, userId, token } = body;

    if (!message || !userId || !token) {
      return new Response(
        JSON.stringify({ error: 'Missing message, userId, or token' }),
        { status: 400, headers: { 'Content-Type': 'application/json' } }
      );
    }

    // Forward the request to the backend chat endpoint with JWT auth
    const backendResponse = await fetch(`http://127.0.0.1:8000/api/${userId}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify({ message }),
    });

    if (!backendResponse.ok) {
      const errorText = await backendResponse.text();
      console.error('Backend error:', backendResponse.status, errorText);
      return new Response(
        JSON.stringify({ error: 'Backend error', details: errorText }),
        { status: backendResponse.status, headers: { 'Content-Type': 'application/json' } }
      );
    }

    const data = await backendResponse.json();

    return new Response(JSON.stringify(data), {
      status: 200,
      headers: { 'Content-Type': 'application/json' },
    });
  } catch (error) {
    console.error('Chat API route error:', error);
    return new Response(
      JSON.stringify({
        error: 'Failed to connect to chat service',
        details: error instanceof Error ? error.message : String(error),
      }),
      { status: 500, headers: { 'Content-Type': 'application/json' } }
    );
  }
}
