import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Code2 } from 'lucide-react';
import { toast } from 'sonner';

const RegisterPage = () => {
  const [formData, setFormData] = useState({
    email: '',
    username: '',
    password: '',
    full_name: '',
  });
  const [loading, setLoading] = useState(false);
  const { register } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      await register(
        formData.email,
        formData.username,
        formData.password,
        formData.full_name
      );
      toast.success('Registration successful!');
      navigate('/problems');
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Registration failed');
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <Link to="/" className="inline-flex items-center gap-2 mb-6">
            <div className="w-10 h-10 bg-gradient-to-br from-primary to-secondary rounded-lg flex items-center justify-center">
              <Code2 className="w-6 h-6 text-white" />
            </div>
            <span className="font-heading font-bold text-3xl bg-clip-text text-transparent bg-gradient-to-r from-primary via-secondary to-accent">
              ifelse
            </span>
          </Link>
          <h1 className="font-heading font-bold text-3xl md:text-4xl mb-2">Create Account</h1>
          <p className="text-muted-foreground">Start your coding interview preparation</p>
        </div>

        <div className="bg-card border border-border/50 rounded-lg p-8 shadow-xl">
          <form onSubmit={handleSubmit} className="space-y-6" data-testid="register-form">
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
              className="w-full bg-primary text-primary-foreground hover:bg-primary/90 shadow-[0_0_20px_rgba(99,102,241,0.5)] transition-all duration-300"
              disabled={loading}
              data-testid="register-submit-btn"
            >
              {loading ? 'Creating account...' : 'Create Account'}
            </Button>
          </form>

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
