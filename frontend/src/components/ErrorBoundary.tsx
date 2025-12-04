
import React, { Component, ErrorInfo, ReactNode } from 'react';
import { AlertTriangle } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface Props {
    children: ReactNode;
    fallback?: ReactNode;
}

interface State {
    hasError: boolean;
    error: Error | null;
    errorInfo: ErrorInfo | null;
}

export class ErrorBoundary extends Component<Props, State> {
    public state: State = {
        hasError: false,
        error: null,
        errorInfo: null
    };

    public static getDerivedStateFromError(error: Error): State {
        return { hasError: true, error, errorInfo: null };
    }

    public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
        console.error('Uncaught error:', error, errorInfo);
        this.setState({ errorInfo });
    }

    public render() {
        if (this.state.hasError) {
            if (this.props.fallback) {
                return this.props.fallback;
            }

            return (
                <div className="flex flex-col items-center justify-center min-h-[400px] p-6 text-center space-y-4 bg-background border rounded-lg shadow-sm">
                    <div className="p-3 rounded-full bg-destructive/10 text-destructive">
                        <AlertTriangle className="w-8 h-8" />
                    </div>
                    <h2 className="text-xl font-semibold">Something went wrong</h2>
                    <p className="text-muted-foreground max-w-md">
                        An error occurred while rendering this component.
                    </p>
                    {this.state.error && (
                        <div className="w-full max-w-lg p-4 mt-4 overflow-auto text-left rounded bg-muted/50 text-xs font-mono border border-border/50">
                            <p className="font-bold text-destructive mb-2">{this.state.error.toString()}</p>
                            {this.state.errorInfo && (
                                <pre className="text-muted-foreground whitespace-pre-wrap">
                                    {this.state.errorInfo.componentStack}
                                </pre>
                            )}
                        </div>
                    )}
                    <Button
                        variant="outline"
                        onClick={() => window.location.reload()}
                        className="mt-4"
                    >
                        Reload Page
                    </Button>
                </div>
            );
        }

        return this.props.children;
    }
}
