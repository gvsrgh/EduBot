import { NextRequest, NextResponse } from 'next/server';

// Shared OTP store (in production, use Redis or database)
const getOtpStore = async () => {
  const { otpStore } = await import('../send-otp/route');
  return otpStore;
};

export async function POST(request: NextRequest) {
  try {
    const { email, otp } = await request.json();

    if (!email || !otp) {
      return NextResponse.json(
        { error: 'Email and OTP are required' },
        { status: 400 }
      );
    }

    const otpStore = await getOtpStore();
    const storedData = otpStore.get(email);

    if (!storedData) {
      return NextResponse.json(
        { error: 'No verification code found. Please request a new one.' },
        { status: 400 }
      );
    }

    // Check if OTP has expired
    if (Date.now() > storedData.expiresAt) {
      otpStore.delete(email);
      return NextResponse.json(
        { error: 'Verification code has expired. Please request a new one.' },
        { status: 400 }
      );
    }

    // Verify OTP
    if (storedData.otp !== otp) {
      return NextResponse.json(
        { error: 'Invalid verification code. Please try again.' },
        { status: 400 }
      );
    }

    // OTP is valid - delete it from store
    otpStore.delete(email);

    return NextResponse.json({
      success: true,
      message: 'Email verified successfully',
      username: storedData.username,
    });
  } catch (error) {
    console.error('Verify OTP error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}
