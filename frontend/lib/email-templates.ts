// Professional Email Templates for EduBot+

export const getOtpEmailTemplate = (otp: string, username: string) => `
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Verify Your Email - EduBot+</title>
</head>
<body style="margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f7fa;">
  <table role="presentation" style="width: 100%; border-collapse: collapse;">
    <tr>
      <td align="center" style="padding: 40px 0;">
        <table role="presentation" style="width: 600px; border-collapse: collapse; background-color: #ffffff; border-radius: 16px; box-shadow: 0 4px 24px rgba(0, 0, 0, 0.1);">
          <!-- Header -->
          <tr>
            <td style="padding: 40px 40px 20px 40px; text-align: center; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 16px 16px 0 0;">
              <h1 style="margin: 0; font-size: 32px; color: #ffffff; font-weight: 700;">🎓 EduBot+</h1>
              <p style="margin: 8px 0 0 0; font-size: 14px; color: rgba(255, 255, 255, 0.9);">Your Intelligent Academic Assistant</p>
            </td>
          </tr>
          
          <!-- Body -->
          <tr>
            <td style="padding: 40px;">
              <h2 style="margin: 0 0 16px 0; font-size: 24px; color: #1a1a2e; font-weight: 600;">Verify Your Email Address</h2>
              <p style="margin: 0 0 24px 0; font-size: 16px; color: #4a5568; line-height: 1.6;">
                Hello <strong>${username}</strong>,
              </p>
              <p style="margin: 0 0 24px 0; font-size: 16px; color: #4a5568; line-height: 1.6;">
                Thank you for registering with EduBot+! To complete your account setup, please use the verification code below:
              </p>
              
              <!-- OTP Box -->
              <div style="background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%); border: 2px dashed #667eea; border-radius: 12px; padding: 24px; text-align: center; margin: 32px 0;">
                <p style="margin: 0 0 8px 0; font-size: 14px; color: #4a5568; text-transform: uppercase; letter-spacing: 1px;">Your Verification Code</p>
                <p style="margin: 0; font-size: 42px; font-weight: 700; letter-spacing: 12px; color: #667eea; font-family: 'Courier New', monospace;">${otp}</p>
              </div>
              
              <p style="margin: 0 0 16px 0; font-size: 14px; color: #718096; line-height: 1.6;">
                ⏱️ This code will expire in <strong>10 minutes</strong> for security purposes.
              </p>
              
              <div style="background-color: #fff8e6; border-left: 4px solid #f6ad55; padding: 16px; border-radius: 0 8px 8px 0; margin: 24px 0;">
                <p style="margin: 0; font-size: 14px; color: #744210;">
                  <strong>🔒 Security Notice:</strong> If you didn't request this code, please ignore this email. Never share this code with anyone.
                </p>
              </div>
            </td>
          </tr>
          
          <!-- Footer -->
          <tr>
            <td style="padding: 24px 40px; background-color: #f8fafc; border-radius: 0 0 16px 16px; text-align: center;">
              <p style="margin: 0 0 8px 0; font-size: 14px; color: #718096;">
                Need help? Contact us at <a href="mailto:support@edubot.com" style="color: #667eea; text-decoration: none;">support@edubot.com</a>
              </p>
              <p style="margin: 0; font-size: 12px; color: #a0aec0;">
                © ${new Date().getFullYear()} EduBot+. All rights reserved.
              </p>
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>
`;

export const getWelcomeEmailTemplate = (username: string, email: string) => `
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Welcome to EduBot+</title>
</head>
<body style="margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f7fa;">
  <table role="presentation" style="width: 100%; border-collapse: collapse;">
    <tr>
      <td align="center" style="padding: 40px 0;">
        <table role="presentation" style="width: 600px; border-collapse: collapse; background-color: #ffffff; border-radius: 16px; box-shadow: 0 4px 24px rgba(0, 0, 0, 0.1);">
          <!-- Header -->
          <tr>
            <td style="padding: 40px 40px 20px 40px; text-align: center; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 16px 16px 0 0;">
              <h1 style="margin: 0; font-size: 32px; color: #ffffff; font-weight: 700;">🎉 Welcome to EduBot+!</h1>
              <p style="margin: 8px 0 0 0; font-size: 14px; color: rgba(255, 255, 255, 0.9);">Your account has been successfully created</p>
            </td>
          </tr>
          
          <!-- Body -->
          <tr>
            <td style="padding: 40px;">
              <p style="margin: 0 0 24px 0; font-size: 18px; color: #1a1a2e; line-height: 1.6;">
                Hello <strong>${username}</strong>! 👋
              </p>
              <p style="margin: 0 0 24px 0; font-size: 16px; color: #4a5568; line-height: 1.6;">
                Congratulations! Your EduBot+ account is now active and ready to use. We're thrilled to have you on board!
              </p>
              
              <!-- Account Info Box -->
              <div style="background: linear-gradient(135deg, #48bb7815 0%, #38a16915 100%); border: 1px solid #48bb78; border-radius: 12px; padding: 24px; margin: 24px 0;">
                <h3 style="margin: 0 0 16px 0; font-size: 16px; color: #276749;">📋 Your Account Details</h3>
                <table style="width: 100%; border-collapse: collapse;">
                  <tr>
                    <td style="padding: 8px 0; font-size: 14px; color: #718096;">Username:</td>
                    <td style="padding: 8px 0; font-size: 14px; color: #1a1a2e; font-weight: 600;">${username}</td>
                  </tr>
                  <tr>
                    <td style="padding: 8px 0; font-size: 14px; color: #718096;">Email:</td>
                    <td style="padding: 8px 0; font-size: 14px; color: #1a1a2e; font-weight: 600;">${email}</td>
                  </tr>
                  <tr>
                    <td style="padding: 8px 0; font-size: 14px; color: #718096;">Account Status:</td>
                    <td style="padding: 8px 0; font-size: 14px; color: #48bb78; font-weight: 600;">✓ Verified & Active</td>
                  </tr>
                </table>
              </div>
              
              <!-- Features -->
              <h3 style="margin: 32px 0 16px 0; font-size: 18px; color: #1a1a2e;">🚀 Get Started with EduBot+</h3>
              
              <table style="width: 100%; border-collapse: collapse;">
                <tr>
                  <td style="padding: 12px; vertical-align: top; width: 50%;">
                    <div style="background-color: #f8fafc; border-radius: 8px; padding: 16px; height: 100%;">
                      <p style="margin: 0 0 8px 0; font-size: 24px;">💬</p>
                      <p style="margin: 0 0 4px 0; font-size: 14px; font-weight: 600; color: #1a1a2e;">Smart Conversations</p>
                      <p style="margin: 0; font-size: 12px; color: #718096;">Get instant answers to your academic queries</p>
                    </div>
                  </td>
                  <td style="padding: 12px; vertical-align: top; width: 50%;">
                    <div style="background-color: #f8fafc; border-radius: 8px; padding: 16px; height: 100%;">
                      <p style="margin: 0 0 8px 0; font-size: 24px;">📚</p>
                      <p style="margin: 0 0 4px 0; font-size: 14px; font-weight: 600; color: #1a1a2e;">Knowledge Base</p>
                      <p style="margin: 0; font-size: 12px; color: #718096;">Access comprehensive academic resources</p>
                    </div>
                  </td>
                </tr>
                <tr>
                  <td style="padding: 12px; vertical-align: top; width: 50%;">
                    <div style="background-color: #f8fafc; border-radius: 8px; padding: 16px; height: 100%;">
                      <p style="margin: 0 0 8px 0; font-size: 24px;">🎯</p>
                      <p style="margin: 0 0 4px 0; font-size: 14px; font-weight: 600; color: #1a1a2e;">Personalized Help</p>
                      <p style="margin: 0; font-size: 12px; color: #718096;">Tailored responses for your needs</p>
                    </div>
                  </td>
                  <td style="padding: 12px; vertical-align: top; width: 50%;">
                    <div style="background-color: #f8fafc; border-radius: 8px; padding: 16px; height: 100%;">
                      <p style="margin: 0 0 8px 0; font-size: 24px;">⚡</p>
                      <p style="margin: 0 0 4px 0; font-size: 14px; font-weight: 600; color: #1a1a2e;">Instant Responses</p>
                      <p style="margin: 0; font-size: 12px; color: #718096;">Get answers in seconds, anytime</p>
                    </div>
                  </td>
                </tr>
              </table>
              
              <!-- CTA Button -->
              <div style="text-align: center; margin: 32px 0;">
                <a href="${process.env.NEXT_PUBLIC_APP_URL || 'http://localhost:3000'}/chat" 
                   style="display: inline-block; padding: 16px 32px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: #ffffff; text-decoration: none; border-radius: 8px; font-size: 16px; font-weight: 600; box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);">
                  Start Chatting Now →
                </a>
              </div>
            </td>
          </tr>
          
          <!-- Footer -->
          <tr>
            <td style="padding: 24px 40px; background-color: #f8fafc; border-radius: 0 0 16px 16px; text-align: center;">
              <p style="margin: 0 0 8px 0; font-size: 14px; color: #718096;">
                Need assistance? We're here to help at <a href="mailto:support@edubot.com" style="color: #667eea; text-decoration: none;">support@edubot.com</a>
              </p>
              <div style="margin: 16px 0;">
                <a href="#" style="display: inline-block; margin: 0 8px; color: #667eea; text-decoration: none; font-size: 12px;">Privacy Policy</a>
                <span style="color: #cbd5e0;">|</span>
                <a href="#" style="display: inline-block; margin: 0 8px; color: #667eea; text-decoration: none; font-size: 12px;">Terms of Service</a>
                <span style="color: #cbd5e0;">|</span>
                <a href="#" style="display: inline-block; margin: 0 8px; color: #667eea; text-decoration: none; font-size: 12px;">Help Center</a>
              </div>
              <p style="margin: 0; font-size: 12px; color: #a0aec0;">
                © ${new Date().getFullYear()} EduBot+. All rights reserved.
              </p>
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>
`;
