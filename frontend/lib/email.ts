import nodemailer from 'nodemailer';
import { getOtpEmailTemplate, getWelcomeEmailTemplate } from './email-templates';

// Create reusable transporter
const createTransporter = () => {
  return nodemailer.createTransport({
    service: 'gmail',
    auth: {
      user: process.env.EMAIL_USER,
      pass: process.env.EMAIL_PASS, // Use App Password for Gmail
    },
  });
};

// Generate 6-digit OTP
export const generateOTP = (): string => {
  return Math.floor(100000 + Math.random() * 900000).toString();
};

// Send OTP email
export const sendOTPEmail = async (
  email: string,
  username: string,
  otp: string
): Promise<boolean> => {
  try {
    const transporter = createTransporter();
    
    const mailOptions = {
      from: {
        name: 'EduBot+',
        address: process.env.EMAIL_USER as string,
      },
      to: email,
      subject: '🔐 Verify Your Email - EduBot+',
      html: getOtpEmailTemplate(otp, username),
    };

    await transporter.sendMail(mailOptions);
    return true;
  } catch (error) {
    console.error('Error sending OTP email:', error);
    return false;
  }
};

// Send welcome/account confirmation email
export const sendWelcomeEmail = async (
  email: string,
  username: string
): Promise<boolean> => {
  try {
    const transporter = createTransporter();
    
    const mailOptions = {
      from: {
        name: 'EduBot+',
        address: process.env.EMAIL_USER as string,
      },
      to: email,
      subject: '🎉 Welcome to EduBot+ - Account Created Successfully!',
      html: getWelcomeEmailTemplate(username, email),
    };

    await transporter.sendMail(mailOptions);
    return true;
  } catch (error) {
    console.error('Error sending welcome email:', error);
    return false;
  }
};
