import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import { GoogleLogin } from '@react-oauth/google';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import IfElseIcon from '@/components/IfElseIcon';
import { toast } from 'sonner';

const OTP_LENGTH = 6;
const GOOGLE_CLIENT_ID = process.env.REACT_APP_GOOGLE_CLIENT_ID;

const RegisterPage = () => {
  const [step, setStep] = useState(1);
  const [formData, setFormData] = useState({
    email: '',
    username: '',
    password: '',
    full_name: '',
  });
  const [otp, setOtp] = useState('');
  const [loading, setLoading] = useState(false);
  const { sendSignupOtp, registerWithOtp, loginWithGoogle } = useAuth();
  const navigate = useNavigate();

  const handleSendOtp = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await sendSignupOtp(formData.email);
      toast.success('Verification code sent to your email');
      setStep(2);
    } catch (error) {
      const msg = error.response?.data?.detail || 'Failed to send code';
      toast.error(Array.isArray(msg) ? msg[0]?.msg ?? msg : msg);
    } finally {
      setLoading(false);
    }
  };

  const handleVerifyAndRegister = async (e) => {
    e.preventDefault();
    const trimmed = otp.replace(/\s/g, '');
    if (trimmed.length !== OTP_LENGTH) {
      toast.error(`Enter a ${OTP_LENGTH}-digit code`);
      return;
    }
    setLoading(true);
    try {
      await registerWithOtp(
        formData.email,
        trimmed,
        formData.username,
        formData.password,
        formData.full_name
      );
      toast.success('Account created successfully!');
      navigate('/problems');
    } catch (error) {
      const msg = error.response?.data?.detail || 'Verification failed';
      toast.error(Array.isArray(msg) ? msg[0]?.msg ?? msg : msg);
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleOtpChange = (e) => {
    const v = e.target.value.replace(/\D/g, '').slice(0, OTP_LENGTH);
    setOtp(v);
  };

  const handleGoogleSuccess = async (credentialResponse) => {
    if (!credentialResponse?.credential) return;
    setLoading(true);
    try {
      await loginWithGoogle(credentialResponse.credential);
      toast.success('Signed up with Google!');
      navigate('/problems');
    } catch (error) {
      const msg = error.response?.data?.detail || 'Google sign-in failed';
      toast.error(Array.isArray(msg) ? msg[0]?.msg ?? msg : msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <Link to="/" className="inline-flex items-center gap-2 mb-6">
            <div className="w-10 h-10 bg-gradient-to-br from-primary to-secondary rounded-lg flex items-center justify-center">
              <IfElseIcon className="w-6 h-6 text-white" />
            </div>
            <span className="font-heading font-bold text-3xl bg-clip-text text-transparent bg-gradient-to-r from-primary via-secondary to-accent">
              If Else
            </span>
          </Link>
          <h1 className="font-heading font-bold text-3xl md:text-4xl mb-2">Create Account</h1>
          <p className="text-muted-foreground">
            {step === 1 ? 'Start your coding interview preparation' : 'Enter the code we sent to your email'}
          </p>
        </div>

        <div className="bg-card border border-border/50 rounded-lg p-8 shadow-xl">
          {step === 1 ? (
            <form onSubmit={handleSendOtp} className="space-y-6" data-testid="register-form">
              <div className="space-y-2">
                <Label htmlFor="email" data-testid="email-label">Email</Label>
                <Input
                  id="email"
                  name="email"
                  type="email"
                  placeholder="you@example.com"
                  value={formData.email}
                  onChange={handleChange}
                  required
                  data-testid="email-input"
                  className="bg-input/50 border-input focus:border-primary focus:ring-primary/30"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="username" data-testid="username-label">Username</Label>
                <Input
                  id="username"
                  name="username"
                  type="text"
                  placeholder="coder123"
                  value={formData.username}
                  onChange={handleChange}
                  required
                  data-testid="username-input"
                  className="bg-input/50 border-input focus:border-primary focus:ring-primary/30"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="full_name" data-testid="fullname-label">Full Name</Label>
                <Input
                  id="full_name"
                  name="full_name"
                  type="text"
                  placeholder="John Doe"
                  value={formData.full_name}
                  onChange={handleChange}
                  data-testid="fullname-input"
                  className="bg-input/50 border-input focus:border-primary focus:ring-primary/30"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="password" data-testid="password-label">Password</Label>
                <Input
                  id="password"
                  name="password"
                  type="password"
                  placeholder="••••••••"
                  value={formData.password}
                  onChange={handleChange}
                  required
                  data-testid="password-input"
                  className="bg-input/50 border-input focus:border-primary focus:ring-primary/30"
                />
              </div>
              <Button
                type="submit"
                className="w-full bg-primary text-primary-foreground hover:bg-primary/90 shadow-[0_0_20px_rgba(37,99,235,0.5)] transition-all duration-300"
                disabled={loading}
                data-testid="register-send-otp-btn"
              >
                {loading ? 'Sending code...' : 'Send verification code'}
              </Button>
              {GOOGLE_CLIENT_ID && (
                <>
                  <div className="relative my-4">
                    <div className="absolute inset-0 flex items-center">
                      <span className="w-full border-t border-border" />
                    </div>
                    <div className="relative flex justify-center text-xs uppercase">
                      <span className="bg-card px-2 text-muted-foreground">or</span>
                    </div>
                  </div>
                  <div className="flex justify-center">
                    <GoogleLogin
                      onSuccess={handleGoogleSuccess}
                      onError={() => toast.error('Google sign-in was cancelled or failed')}
                      theme="filled_black"
                      size="large"
                      text="signup_with"
                      width="320"
                    />
                  </div>
                </>
              )}
            </form>
          ) : (
            <form onSubmit={handleVerifyAndRegister} className="space-y-6" data-testid="verify-otp-form">
              <p className="text-sm text-muted-foreground">
                We sent a {OTP_LENGTH}-digit code to <strong>{formData.email}</strong>
              </p>
              <div className="space-y-2">
                <Label htmlFor="otp">Verification code</Label>
                <Input
                  id="otp"
                  type="text"
                  inputMode="numeric"
                  autoComplete="one-time-code"
                  placeholder="000000"
                  value={otp}
                  onChange={handleOtpChange}
                  maxLength={OTP_LENGTH}
                  className="bg-input/50 border-input focus:border-primary focus:ring-primary/30 text-center text-lg tracking-[0.5em]"
                  data-testid="otp-input"
                />
              </div>
              <Button
                type="submit"
                className="w-full bg-primary text-primary-foreground hover:bg-primary/90 shadow-[0_0_20px_rgba(37,99,235,0.5)] transition-all duration-300"
                disabled={loading || otp.length !== OTP_LENGTH}
                data-testid="register-verify-btn"
              >
                {loading ? 'Creating account...' : 'Verify & Create account'}
              </Button>
              <button
                type="button"
                onClick={() => setStep(1)}
                className="w-full text-sm text-muted-foreground hover:text-foreground"
              >
                Use a different email
              </button>
            </form>
          )}

          <div className="mt-6 text-center text-sm">
            <span className="text-muted-foreground">Already have an account? </span>
            <Link to="/login" className="text-primary hover:underline" data-testid="login-link">
              Login
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RegisterPage;
