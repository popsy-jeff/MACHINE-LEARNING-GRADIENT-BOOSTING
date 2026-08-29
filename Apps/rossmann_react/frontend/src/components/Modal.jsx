import { useEffect } from 'react';
import { X, XCircle, AlertTriangle, CheckCircle2, Info } from 'lucide-react';

const TYPE_ICON = {
  red: XCircle,
  orange: AlertTriangle,
  green: CheckCircle2,
  blue: Info,
};

/**
 * A centered modal card with a colored accent (red/orange by default, but
 * green/blue also supported for flexibility). Closes on Escape, backdrop
 * click, or the close button.
 */
export default function Modal({ open, onClose, title, type = 'red', children, footer }) {
  useEffect(() => {
    if (!open) return;
    function onKeyDown(e) {
      if (e.key === 'Escape') onClose?.();
    }
    document.addEventListener('keydown', onKeyDown);
    return () => document.removeEventListener('keydown', onKeyDown);
  }, [open, onClose]);

  if (!open) return null;

  const Icon = TYPE_ICON[type] || AlertTriangle;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div
        className={`modal-card modal-${type}`}
        role="dialog"
        aria-modal="true"
        aria-label={title}
        onClick={(e) => e.stopPropagation()}
      >
        <div className="modal-header">
          <div className="modal-header-title">
            <Icon size={20} />
            <span>{title}</span>
          </div>
          <button type="button" className="modal-close" onClick={onClose} aria-label="Close">
            <X size={18} />
          </button>
        </div>
        <div className="modal-body">{children}</div>
        {footer && <div className="modal-footer">{footer}</div>}
      </div>
    </div>
  );
}
