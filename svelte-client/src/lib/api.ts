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

        const data = await response.json(); if (response.ok) {
            const result = { success: true, data: { summary: data.summary } };
            return result;
        } else {
            const errorResult = { success: false, error: data.error || 'Failed to get summary' };
            return errorResult;
        }
    } catch (error) {
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
    onChunk?: (chunk: string) => void,
    conversationHistory?: Array<{ type: string; content: string; }>
): Promise<ApiResponse<{ reply: string; }>> {
    try {
        const requestBody: {
            message: string;
            images?: string[];
            stream?: boolean;
            conversation_history?: Array<{ type: string; content: string; }>;
        } = {
            message,
            stream: !!onChunk  // Enable streaming if onChunk callback is provided
        };

        // If images are provided, include them in the request
        if (images && images.length > 0) {
            requestBody.images = images;
        }

        // If conversation history is provided, include it in the request
        if (conversationHistory && conversationHistory.length > 0) {
            requestBody.conversation_history = conversationHistory;
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
        }        // Handle streaming response (but server doesn't actually support it yet)
        // For now, always handle as non-streaming and simulate typewriter effect if needed
        const data = await response.json();

        if (onChunk && data.reply) {
            // Simulate typewriter effect by breaking the response into chunks
            const words = data.reply.split(' ');
            let currentText = '';

            for (let i = 0; i < words.length; i++) {
                currentText += (i > 0 ? ' ' : '') + words[i];
                onChunk(i > 0 ? ' ' + words[i] : words[i]);
                // Small delay to simulate streaming
                await new Promise(resolve => setTimeout(resolve, 50));
            }
        }

        const result = { success: true, data: { reply: data.reply } };
        return result;
    } catch (error) {
        return {
            success: false,
            error: 'Failed to connect to server. Please make sure the server is running.'
        };
    }
}
