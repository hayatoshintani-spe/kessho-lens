'use client';

import ReactMarkdown from 'react-markdown';

interface MarkdownReportProps {
  content: string;
  className?: string;
}

export default function MarkdownReport({ content, className }: MarkdownReportProps) {
  return (
    <div className={`markdown-report ${className ?? ''}`}>
      <ReactMarkdown>{content}</ReactMarkdown>
    </div>
  );
}
