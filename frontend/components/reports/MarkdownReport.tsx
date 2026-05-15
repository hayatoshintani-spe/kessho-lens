'use client';

import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

interface MarkdownReportProps {
  content: string;
  className?: string;
}

export default function MarkdownReport({ content, className }: MarkdownReportProps) {
  return (
    <div className={`markdown-report ${className ?? ''}`}>
      <ReactMarkdown remarkPlugins={[remarkGfm]}>{content}</ReactMarkdown>
    </div>
  );
}
