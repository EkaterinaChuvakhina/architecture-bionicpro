import React, { useState, useEffect } from 'react';

const ReportPage: React.FC = () => {
    const [authenticated, setAuthenticated] = useState(false);
    const [checkingAuth, setCheckingAuth] = useState(true);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const authUrl = process.env.REACT_APP_AUTH_URL || 'http://localhost:8081';
    const backendUrl = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8083';

    useEffect(() => {
        const checkAuth = async () => {
            try {
                const res = await fetch(`${authUrl}/api/auth/status`, {
                    credentials: 'include',   // обязательно!
                });

                if (!res.ok) {
                    throw new Error('Not authenticated');
                }

                const data = await res.json();
                setAuthenticated(data.authenticated);
            } catch {
                setAuthenticated(false);
            } finally {
                setCheckingAuth(false);
            }
        };

        checkAuth();
    }, [authUrl]);

    const loginWithKeycloak = () => {
        window.location.href = `${authUrl}/oauth2/authorization/bionicpro-auth`;
    };

    const loginWithYandex = () => {
        window.location.href = `${authUrl}/oauth2/authorization/bionicpro-auth?kc_idp_hint=yandex`;
    };

    const downloadReport = async () => {
        setLoading(true);
        setError(null);

        try {
            const res = await fetch(`${backendUrl}/reports/`, {
                credentials: 'include',
            });

            if (!res.ok) {
                if (res.status === 401 || res.status === 403) {
                    setAuthenticated(false);
                    throw new Error('Session expired. Please log in again.');
                }
                throw new Error('Failed to get report');
            }

            const data = await res.json();

            if (data.download_url) {
                const link = document.createElement('a');
                link.href = data.download_url;
                link.download = `bionicpro-report-${new Date().toISOString().slice(0, 10)}.pdf`;
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
            } else {
                throw new Error('No download link received');
            }

        } catch (err: any) {
            setError(err.message || 'An error occurred');
        } finally {
            setLoading(false);
        }
    };

    if (checkingAuth) {
        return <div>Loading...</div>;
    }

    if (!authenticated) {
        return (
            <div className="flex flex-col items-center justify-center min-h-screen bg-gray-100">
                <div className="p-8 bg-white rounded-lg shadow-md text-center">
                    <h2 className="text-2xl font-bold mb-6">Sign In</h2>

                    <button
                        onClick={loginWithKeycloak}
                        className="w-full px-6 py-3 mb-4 bg-blue-600 text-white rounded hover:bg-blue-700 text-lg font-medium"
                    >
                        Login with Keycloak
                    </button>

                    <button
                        onClick={loginWithYandex}
                        className="w-full px-6 py-3 bg-yellow-500 text-white rounded hover:bg-yellow-600 text-lg font-medium"
                    >
                        Login with Yandex ID
                    </button>

                    {error && (
                        <div className="mt-4 p-4 bg-red-100 text-red-700 rounded">
                            {error}
                        </div>
                    )}
                </div>
            </div>
        );
    }

    return (
        <div className="flex flex-col items-center justify-center min-h-screen bg-gray-100">
            <div className="p-8 bg-white rounded-lg shadow-md text-center">
                <h1 className="text-3xl font-bold mb-8">Usage Reports</h1>

                <button
                    onClick={downloadReport}
                    disabled={loading}
                    className={`px-8 py-4 bg-green-600 text-white rounded-lg hover:bg-green-700 text-lg font-semibold ${
                        loading ? 'opacity-50 cursor-not-allowed' : ''
                    }`}
                >
                    {loading ? 'Generating Report...' : 'Download Report'}
                </button>

                {error && (
                    <div className="mt-6 p-4 bg-red-100 text-red-700 rounded-lg">
                        {error}
                    </div>
                )}
            </div>
        </div>
    );
};

export default ReportPage;