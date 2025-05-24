const API_BASE = 'http://localhost:5000/api';

export interface ApiResponse<T> {
    success: boolean;
    data?: T;
    error?: string;
}

export async function summarizeVideo(url: string): Promise<ApiResponse<{ summary: string; }>> {
    try {
        const response = await fetch(`${API_BASE}/summarize`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ youtube_url: url }),
        });

        const data = await response.json();
        if (response.ok) {
            return { success: true, data: { summary: data.summary } };
        } else {
            return { success: false, error: data.error || 'Failed to get summary' };
        }
    } catch {
        return {
            success: false,
            error: 'Failed to connect to server. Please make sure the server is running.'
        };
    }
}

export async function explainVideo(url: string): Promise<ApiResponse<{ explanation: string; }>> {
    try {
        const response = await fetch(`${API_BASE}/explain`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ youtube_url: url }),
        });

        const data = await response.json();
        if (response.ok) {
            return { success: true, data: { explanation: data.explanation } };
        } else {
            return { success: false, error: data.error || 'Failed to get explanation' };
        }
    } catch {
        return {
            success: false,
            error: 'Failed to connect to server. Please make sure the server is running.'
        };
    }
}

export async function sendChatMessage(message: string, images?: string[]): Promise<ApiResponse<{ reply: string; }>> {
    try {
        const requestBody: { message: string; images?: string[]; } = { message };

        // If images are provided, include them in the request
        if (images && images.length > 0) {
            requestBody.images = images;
        }

        const response = await fetch(`${API_BASE}/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestBody),
        });

        const data = await response.json();
        if (response.ok) {
            return { success: true, data: { reply: data.reply } };
        } else {
            return { success: false, error: data.error || 'Failed to get response' };
        }
    } catch {
        return {
            success: false,
            error: 'Failed to connect to server. Please make sure the server is running.'
        };
    }
}
