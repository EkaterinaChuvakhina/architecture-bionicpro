import React, { useState, useEffect } from 'react';

const ReportPage: React.FC = () => {
    const [authenticated, setAuthenticated] = useState(false);
    const [checkingAuth, setCheckingAuth] = useState(true);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const backendUrl = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8081';
    const keycloakUrl = process.env.REACT_APP_KEYCLOAK_URL || 'http://localhost:8080';
    const realm = process.env.REACT_APP_KEYCLOAK_REALM || 'reports-realm';
    const clientId = process.env.REACT_APP_KEYCLOAK_CLIENT_ID || 'reports-frontend';

    // Базовый URL для Keycloak авторизации
    const keycloakAuthUrl = `${keycloakUrl}/realms/${realm}/protocol/openid-connect/auth`;

    useEffect(() => {
        const checkAuth = async () => {
            try {
                const res = await fetch(`${backendUrl}/api/auth/status`, {
                    credentials: 'include',
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
    }, [backendUrl]);

    const loginWithKeycloak = () => {
        // Старый способ логина — без изменений
        window.location.href = `${backendUrl}/oauth2/authorization/bionicpro-auth`;
    };

    const loginWithYandex = () => {
        // Вход через Яндекс ID (Identity Brokering)
        const redirectUri = encodeURIComponent(window.location.origin);
        window.location.href = `${backendUrl}/oauth2/authorization/bionicpro-auth?kc_idp_hint=yandex`;
    };

    const downloadReport = async () => {
        setLoading(true);
        setError(null);

        try {
            const res = await fetch(`${backendUrl}/reports`, {
                credentials: 'include',
            });

            if (!res.ok) {
                if (res.status === 401 || res.status === 403) {
                    setAuthenticated(false);
                    throw new Error('Сессия истекла. Пожалуйста, войдите заново.');
                }
                throw new Error('Не удалось скачать отчёт');
            }

            const blob = await res.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'report.pdf';
            document.body.appendChild(a);
            a.click();
            a.remove();
            window.URL.revokeObjectURL(url);
        } catch (err: any) {
            setError(err.message || 'Произошла ошибка');
        } finally {
            setLoading(false);
        }
    };

    if (checkingAuth) {
        return <div>Загрузка...</div>;
    }

    if (!authenticated) {
        return (
            <div className="flex flex-col items-center justify-center min-h-screen bg-gray-100">
                <div className="p-8 bg-white rounded-lg shadow-md text-center">
                    <h2 className="text-2xl font-bold mb-6">Вход в систему</h2>

                    <button
                        onClick={loginWithKeycloak}
                        className="w-full px-6 py-3 mb-4 bg-blue-600 text-white rounded hover:bg-blue-700 text-lg font-medium"
                    >
                        Login
                    </button>

                    <button
                        onClick={loginWithYandex}
                        className="w-full px-6 py-3 bg-yellow-500 text-white rounded hover:bg-yellow-600 text-lg font-medium"
                    >
                        Войти через Яндекс ID
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
                    {loading ? 'Генерация отчёта...' : 'Скачать отчёт (PDF)'}
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