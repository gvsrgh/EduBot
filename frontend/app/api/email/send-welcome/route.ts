import { NextRequest, NextResponse } from 'next/server';
import { sendWelcomeEmail } from '@/lib/email';

export async function POST(request: NextRequest) {
  try {
    const { email, username } = await request.json();

    if (!email || !username) {
      return NextResponse.json(
        { error: 'Email and username are required' },
        { status: 400 }
      );
    }

    // Send welcome email
    const sent = await sendWelcomeEmail(email, username);

    if (!sent) {
      // Don't fail registration if welcome email fails
      console.error('Failed to send welcome email');
      return NextResponse.json({
        success: true,
        message: 'Account created (welcome email could not be sent)',
      });
    }

    return NextResponse.json({
      success: true,
      message: 'Welcome email sent successfully',
    });
  } catch (error) {
    console.error('Send welcome email error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}
