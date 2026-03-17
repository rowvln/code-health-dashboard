/**
 * CollapsiblePanel
 *
 * Reusable UI component for sections that can be expanded/collapsed.
 *
 * Purpose:
 * - improve readability of large datasets (issues, files, etc.)
 * - allow users to focus on relevant sections
 *
 * Design:
 * - controlled locally via internal state
 * - defaults to open for visibility
 *
 * Future improvements:
 * - persist collapse state
 * - add "expand all / collapse all"
 */
import { useState } from 'react'

export default function CollapsiblePanel({
  title,
  children,
  defaultOpen = true,
  description = '',
}) {
  const [isOpen, setIsOpen] = useState(defaultOpen)

  return (
    <section className="panel panel-wide collapsible-panel">
      <button
        type="button"
        className="collapsible-header"
        onClick={() => setIsOpen((prev) => !prev)}
        aria-expanded={isOpen}
      >
        <div className="collapsible-header-text">
          <h2>{title}</h2>
          {description && <p className="section-description">{description}</p>}
        </div>

        <span className={`collapse-icon ${isOpen ? 'open' : ''}`}>
          {isOpen ? '−' : '+'}
        </span>
      </button>

      {isOpen && <div className="collapsible-content">{children}</div>}
    </section>
  )
}