import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import api from '@/utils/api';
import { Button } from '@/components/ui/button';
import { Code2, LogOut, User, Filter } from 'lucide-react';
import { DIFFICULTY_COLORS, DIFFICULTY_BG } from '@/utils/constants';
import { toast } from 'sonner';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';

const ProblemsPage = () => {
  const [problems, setProblems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [difficulty, setDifficulty] = useState('all');
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (!user) {
      navigate('/login');
      return;
    }
    fetchProblems();
  }, [user, difficulty]);

  const fetchProblems = async () => {
    try {
      const params = difficulty !== 'all' ? { difficulty } : {};
      const response = await api.get('/problems', { params });
      setProblems(response.data);
    } catch (error) {
      toast.error('Failed to load problems');
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/');
    toast.success('Logged out successfully');
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Navbar */}
      <nav className="border-b border-border/50 backdrop-blur-xl bg-background/60 sticky top-0 z-50">
        <div className="container mx-auto px-6 md:px-12 lg:px-24 py-4">
          <div className="flex items-center justify-between">
            <Link to="/" className="flex items-center gap-2">
              <div className="w-8 h-8 bg-gradient-to-br from-primary to-secondary rounded-lg flex items-center justify-center">
                <Code2 className="w-5 h-5 text-white" />
              </div>
              <span className="font-heading font-bold text-2xl bg-clip-text text-transparent bg-gradient-to-r from-primary via-secondary to-accent">
                ifelse
              </span>
            </Link>
            <div className="flex items-center gap-4">
              <Link to="/dashboard" data-testid="nav-dashboard-link">
                <Button variant="ghost" className="text-muted-foreground hover:text-foreground">
                  <User className="w-4 h-4 mr-2" />
                  {user?.username}
                </Button>
              </Link>
              <Button
                variant="outline"
                onClick={handleLogout}
                data-testid="logout-btn"
                className="border-input hover:bg-destructive hover:text-destructive-foreground"
              >
                <LogOut className="w-4 h-4 mr-2" />
                Logout
              </Button>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <div className="container mx-auto px-6 md:px-12 lg:px-24 py-12">
        <div className="mb-8">
          <h1 className="font-heading font-bold text-4xl md:text-5xl mb-4">
            Practice Problems
          </h1>
          <div className="flex items-center gap-4">
            <Filter className="w-5 h-5 text-muted-foreground" />
            <Select value={difficulty} onValueChange={setDifficulty} data-testid="difficulty-filter">
              <SelectTrigger className="w-48 bg-card border-border">
                <SelectValue placeholder="Difficulty" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Difficulties</SelectItem>
                <SelectItem value="easy">Easy</SelectItem>
                <SelectItem value="medium">Medium</SelectItem>
                <SelectItem value="hard">Hard</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>

        {loading ? (
          <div className="text-center py-12">
            <p className="text-muted-foreground">Loading problems...</p>
          </div>
        ) : problems.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-muted-foreground">No problems found</p>
          </div>
        ) : (
          <div className="bg-card border border-border/50 rounded-lg overflow-hidden shadow-xl" data-testid="problems-list">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-muted/30 border-b border-border">
                  <tr>
                    <th className="px-6 py-4 text-left text-sm font-heading font-semibold">
                      Title
                    </th>
                    <th className="px-6 py-4 text-left text-sm font-heading font-semibold">
                      Difficulty
                    </th>
                    <th className="px-6 py-4 text-left text-sm font-heading font-semibold">
                      Acceptance
                    </th>
                    <th className="px-6 py-4 text-left text-sm font-heading font-semibold">
                      Tags
                    </th>
                    <th className="px-6 py-4"></th>
                  </tr>
                </thead>
                <tbody>
                  {problems.map((problem) => (
                    <tr
                      key={problem.id}
                      className="border-b border-border/30 hover:bg-muted/20 transition-colors"
                      data-testid={`problem-row-${problem.id}`}
                    >
                      <td className="px-6 py-4">
                        <Link
                          to={`/problems/${problem.id}`}
                          className="font-medium hover:text-primary transition-colors"
                          data-testid={`problem-title-${problem.id}`}
                        >
                          {problem.title}
                        </Link>
                      </td>
                      <td className="px-6 py-4">
                        <span
                          className={`inline-flex px-3 py-1 rounded-full text-sm font-medium border ${DIFFICULTY_BG[problem.difficulty]} ${DIFFICULTY_COLORS[problem.difficulty]}`}
                        >
                          {problem.difficulty.charAt(0).toUpperCase() + problem.difficulty.slice(1)}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-muted-foreground">
                        {problem.total_submissions > 0
                          ? `${Math.round((problem.accepted_submissions / problem.total_submissions) * 100)}%`
                          : 'N/A'}
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex flex-wrap gap-2">
                          {problem.tags.slice(0, 2).map((tag) => (
                            <span
                              key={tag}
                              className="text-xs px-2 py-1 bg-accent/10 text-accent rounded"
                            >
                              {tag}
                            </span>
                          ))}
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <Link to={`/problems/${problem.id}`} data-testid={`solve-btn-${problem.id}`}>
                          <Button
                            size="sm"
                            className="bg-primary text-primary-foreground hover:bg-primary/90"
                          >
                            Solve
                          </Button>
                        </Link>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ProblemsPage;
