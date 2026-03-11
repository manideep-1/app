import React, { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import { GoogleLogin } from '@react-oauth/google';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import IfElseIcon from '@/components/IfElseIcon';
import { toast } from 'sonner';

const GOOGLE_CLIENT_ID = process.env.REACT_APP_GOOGLE_CLIENT_ID;

const LoginPage = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const { login, loginWithGoogle } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const from = location.state?.from || '/problems';

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      await login(email, password);
      toast.success('Login successful!');
      navigate(from, { replace: true });
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  const handleGoogleSuccess = async (credentialResponse) => {
    if (!credentialResponse?.credential) return;
    setLoading(true);
    try {
      await loginWithGoogle(credentialResponse.credential);
      toast.success('Login successful!');
      navigate(from, { replace: true });
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
          <h1 className="font-heading font-bold text-3xl md:text-4xl mb-2">Welcome Back</h1>
          <p className="text-muted-foreground">Login to continue your coding journey</p>
        </div>

        <div className="bg-card border border-border/50 rounded-lg p-8 shadow-xl">
          <form onSubmit={handleSubmit} className="space-y-6" data-testid="login-form">
            <div className="space-y-2">
              <Label htmlFor="email" data-testid="email-label">Email</Label>
              <Input
                id="email"
                type="email"
                placeholder="you@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                data-testid="email-input"
                className="bg-input/50 border-input focus:border-primary focus:ring-primary/30"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="password" data-testid="password-label">Password</Label>
              <Input
                id="password"
                type="password"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                data-testid="password-input"
                className="bg-input/50 border-input focus:border-primary focus:ring-primary/30"
              />
            </div>
            <Button
              type="submit"
              className="w-full bg-primary text-primary-foreground hover:bg-primary/90 shadow-[0_0_20px_rgba(37,99,235,0.5)] transition-all duration-300"
              disabled={loading}
              data-testid="login-submit-btn"
            >
              {loading ? 'Logging in...' : 'Login'}
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
                    text="signin_with"
                    width="320"
                  />
                </div>
              </>
            )}
          </form>

          <div className="mt-6 text-center text-sm">
            <span className="text-muted-foreground">Don't have an account? </span>
            <Link to="/register" className="text-primary hover:underline" data-testid="register-link">
              Sign up
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
