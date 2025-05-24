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

export async function sendChatMessage(
    message: string,
    images?: string[],
    onChunk?: (chunk: string) => void
): Promise<ApiResponse<{ reply: string; }>> {
    try {
        const requestBody: { message: string; images?: string[]; stream?: boolean; } = {
            message,
            stream: !!onChunk  // Enable streaming if onChunk callback is provided
        };

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

        if (!response.ok) {
            const errorData = await response.json();
            return { success: false, error: errorData.error || 'Failed to get response' };
        }

        // Handle streaming response
        if (onChunk && response.body) {
            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let fullReply = '';

            try {
                while (true) {
                    const { done, value } = await reader.read();
                    if (done) break;

                    const chunk = decoder.decode(value, { stream: true });
                    const lines = chunk.split('\n');

                    for (const line of lines) {
                        if (line.startsWith('data: ')) {
                            try {
                                const data = JSON.parse(line.slice(6));
                                if (data.chunk) {
                                    fullReply += data.chunk;
                                    onChunk(data.chunk);
                                }
                                if (data.done) {
                                    return { success: true, data: { reply: fullReply } };
                                }
                            } catch {
                                // Ignore JSON parse errors for malformed chunks
                                console.warn('Failed to parse chunk:', line);
                            }
                        }
                    }
                }

                return { success: true, data: { reply: fullReply } };
            } finally {
                reader.releaseLock();
            }
        } else {
            // Handle non-streaming response
            const data = await response.json();
            return { success: true, data: { reply: data.reply } };
        }
    } catch (error) {
        console.error('Chat API error:', error);
        return {
            success: false,
            error: 'Failed to connect to server. Please make sure the server is running.'
        };
    }
}
