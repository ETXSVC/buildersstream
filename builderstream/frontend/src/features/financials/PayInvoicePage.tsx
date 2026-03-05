/**
 * Public payment page for client invoice payments.
 * Accessible at /pay/:token — no authentication required.
 * Loads Stripe.js from CDN and uses vanilla Stripe Elements.
 */
import { useEffect, useRef, useState } from 'react';
import { useParams } from 'react-router-dom';
import { apiClient } from '@/api/client';

// ── Types ────────────────────────────────────────────────────────────────────

interface PublicInvoice {
  invoice_number: string;
  invoice_type: string;
  status: string;
  organization_name: string;
  project_name: string;
  client_name: string;
  issue_date: string;
  due_date: string;
  subtotal: string;
  tax_amount: string;
  total: string;
  amount_paid: string;
  balance_due: string;
  terms: string;
  notes: string;
  is_paid: boolean;
  line_items: {
    description: string;
    quantity: string;
    unit: string;
    unit_price: string;
    line_total: string;
  }[];
}

// Stripe.js types (loaded from CDN)
declare global {
  interface Window {
    Stripe?: (publishableKey: string) => StripeInstance;
  }
}
interface StripeInstance {
  elements: (options?: object) => StripeElements;
  confirmCardPayment: (clientSecret: string, data: object) => Promise<{ error?: { message: string }; paymentIntent?: { status: string } }>;
}
interface StripeElements {
  create: (type: string, options?: object) => StripeElement;
}
interface StripeElement {
  mount: (selector: string | HTMLElement) => void;
  unmount: () => void;
  on: (event: string, handler: (e: { error?: { message: string } }) => void) => void;
}

// ── Helpers ──────────────────────────────────────────────────────────────────

function loadStripeJs(publishableKey: string): Promise<StripeInstance> {
  return new Promise((resolve, reject) => {
    if (window.Stripe) {
      resolve(window.Stripe(publishableKey));
      return;
    }
    const script = document.createElement('script');
    script.src = 'https://js.stripe.com/v3/';
    script.onload = () => {
      if (window.Stripe) {
        resolve(window.Stripe(publishableKey));
      } else {
        reject(new Error('Stripe.js failed to load'));
      }
    };
    script.onerror = () => reject(new Error('Failed to load Stripe.js'));
    document.head.appendChild(script);
  });
}

function fmt(value: string) {
  return parseFloat(value).toLocaleString('en-US', {
    style: 'currency',
    currency: 'USD',
  });
}

// ── Component ─────────────────────────────────────────────────────────────────

type PageState = 'loading' | 'ready' | 'processing' | 'success' | 'error' | 'not_found' | 'already_paid';

export function PayInvoicePage() {
  const { token } = useParams<{ token: string }>();
  const [invoice, setInvoice] = useState<PublicInvoice | null>(null);
  const [pageState, setPageState] = useState<PageState>('loading');
  const [errorMessage, setErrorMessage] = useState('');
  const [cardError, setCardError] = useState('');

  const stripeRef = useRef<StripeInstance | null>(null);
  const elementsRef = useRef<StripeElements | null>(null);
  const cardRef = useRef<StripeElement | null>(null);
  const cardMountRef = useRef<HTMLDivElement | null>(null);

  // ── Fetch invoice ────────────────────────────────────────────────────────

  useEffect(() => {
    if (!token) return;
    apiClient
      .get(`/api/v1/financials/public/invoices/${token}/`)
      .then(({ data }) => {
        setInvoice(data as PublicInvoice);
        if (data.is_paid) {
          setPageState('already_paid');
        } else {
          setPageState('ready');
        }
      })
      .catch((err) => {
        if (err.response?.status === 404 || err.response?.status === 410) {
          setPageState('not_found');
        } else {
          setErrorMessage('Failed to load invoice. Please try again.');
          setPageState('error');
        }
      });
  }, [token]);

  // ── Mount Stripe card element when page is ready ─────────────────────────

  useEffect(() => {
    if (pageState !== 'ready' || !cardMountRef.current) return;

    const publishableKey = import.meta.env.VITE_STRIPE_PUBLISHABLE_KEY || '';
    if (!publishableKey) {
      setErrorMessage('Payment configuration is missing. Please contact support.');
      setPageState('error');
      return;
    }

    let cancelled = false;
    loadStripeJs(publishableKey)
      .then((stripe) => {
        if (cancelled) return;
        stripeRef.current = stripe;
        const elements = stripe.elements({ locale: 'en' });
        elementsRef.current = elements;
        const card = elements.create('card', {
          style: {
            base: {
              fontSize: '16px',
              color: '#1e293b',
              fontFamily: '"Inter", system-ui, sans-serif',
              '::placeholder': { color: '#94a3b8' },
            },
            invalid: { color: '#ef4444' },
          },
        });
        cardRef.current = card;
        if (cardMountRef.current) {
          card.mount(cardMountRef.current);
          card.on('change', (e) => {
            setCardError(e.error ? e.error.message : '');
          });
        }
      })
      .catch(() => {
        if (!cancelled) {
          setErrorMessage('Payment system could not be loaded. Please try again later.');
          setPageState('error');
        }
      });

    return () => {
      cancelled = true;
      cardRef.current?.unmount();
    };
  }, [pageState]);

  // ── Submit payment ────────────────────────────────────────────────────────

  async function handlePay() {
    if (!stripeRef.current || !cardRef.current || !token) return;
    setPageState('processing');
    setErrorMessage('');

    try {
      const { data } = await apiClient.post(
        `/api/v1/financials/public/invoices/${token}/pay/`,
        {},
      );
      const { client_secret } = data as { client_secret: string };

      const result = await stripeRef.current.confirmCardPayment(client_secret, {
        payment_method: { card: cardRef.current },
      });

      if (result.error) {
        setErrorMessage(result.error.message || 'Payment failed.');
        setPageState('ready');
      } else if (result.paymentIntent?.status === 'succeeded') {
        setPageState('success');
      } else {
        setErrorMessage('Payment was not completed. Please try again.');
        setPageState('ready');
      }
    } catch {
      setErrorMessage('Payment failed. Please try again or contact support.');
      setPageState('ready');
    }
  }

  // ── Render ────────────────────────────────────────────────────────────────

  if (pageState === 'loading') {
    return (
      <div className="flex min-h-screen items-center justify-center bg-slate-50">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-indigo-600 border-t-transparent" />
      </div>
    );
  }

  if (pageState === 'not_found') {
    return (
      <PublicShell>
        <div className="py-16 text-center">
          <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-slate-100">
            <svg className="h-8 w-8 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <h2 className="text-xl font-semibold text-slate-900">Invoice Not Found</h2>
          <p className="mt-2 text-sm text-slate-500">
            This invoice link may have expired or been voided. Please contact your contractor.
          </p>
        </div>
      </PublicShell>
    );
  }

  if (pageState === 'already_paid') {
    return (
      <PublicShell>
        <div className="py-12 text-center">
          <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-green-100">
            <svg className="h-8 w-8 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <h2 className="text-xl font-semibold text-slate-900">Invoice Already Paid</h2>
          <p className="mt-2 text-sm text-slate-500">
            Invoice {invoice?.invoice_number} has already been paid in full. Thank you!
          </p>
          {invoice && (
            <div className="mt-6 inline-block rounded-xl border border-slate-200 bg-white px-8 py-4 text-left">
              <p className="text-sm text-slate-500">{invoice.organization_name}</p>
              <p className="mt-1 text-lg font-semibold text-slate-900">
                {invoice.invoice_number}
              </p>
              <p className="mt-1 text-sm text-slate-600">{invoice.project_name}</p>
              <p className="mt-2 text-2xl font-bold text-green-600">{fmt(invoice.total)} paid</p>
            </div>
          )}
        </div>
      </PublicShell>
    );
  }

  if (pageState === 'success') {
    return (
      <PublicShell>
        <div className="py-12 text-center">
          <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-green-100">
            <svg className="h-8 w-8 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <h2 className="text-2xl font-bold text-slate-900">Payment Successful!</h2>
          <p className="mt-2 text-slate-500">
            Thank you — your payment has been received. A receipt will be sent to your email.
          </p>
          {invoice && (
            <p className="mt-4 text-sm font-medium text-slate-700">
              {invoice.invoice_number} · {fmt(invoice.balance_due)}
            </p>
          )}
        </div>
      </PublicShell>
    );
  }

  if (pageState === 'error' && !invoice) {
    return (
      <PublicShell>
        <div className="py-16 text-center">
          <p className="text-red-600">{errorMessage || 'An unexpected error occurred.'}</p>
        </div>
      </PublicShell>
    );
  }

  // ── Main payment UI ───────────────────────────────────────────────────────

  const isProcessing = pageState === 'processing';

  return (
    <PublicShell>
      {invoice && (
        <div className="grid gap-6 md:grid-cols-2">
          {/* Invoice Summary */}
          <div className="rounded-xl border border-slate-200 bg-white p-6">
            <div className="mb-4 border-b border-slate-100 pb-4">
              <p className="text-xs font-semibold uppercase tracking-wider text-slate-400">
                {invoice.organization_name}
              </p>
              <h2 className="mt-1 text-xl font-bold text-slate-900">{invoice.invoice_number}</h2>
              <p className="text-sm text-slate-500">{invoice.project_name}</p>
            </div>

            {/* Line items */}
            <div className="space-y-2">
              {invoice.line_items.map((item, i) => (
                <div key={i} className="flex items-start justify-between gap-4">
                  <div className="min-w-0 flex-1">
                    <p className="truncate text-sm text-slate-700">{item.description}</p>
                    <p className="text-xs text-slate-400">
                      {item.quantity} {item.unit} × {fmt(item.unit_price)}
                    </p>
                  </div>
                  <p className="flex-shrink-0 text-sm font-medium text-slate-900">
                    {fmt(item.line_total)}
                  </p>
                </div>
              ))}
            </div>

            {/* Totals */}
            <div className="mt-4 space-y-1 border-t border-slate-100 pt-4 text-sm">
              <div className="flex justify-between text-slate-500">
                <span>Subtotal</span>
                <span>{fmt(invoice.subtotal)}</span>
              </div>
              {parseFloat(invoice.tax_amount) > 0 && (
                <div className="flex justify-between text-slate-500">
                  <span>Tax</span>
                  <span>{fmt(invoice.tax_amount)}</span>
                </div>
              )}
              {parseFloat(invoice.amount_paid) > 0 && (
                <div className="flex justify-between text-slate-500">
                  <span>Amount Paid</span>
                  <span>−{fmt(invoice.amount_paid)}</span>
                </div>
              )}
              <div className="flex justify-between border-t border-slate-200 pt-2 font-semibold text-slate-900">
                <span>Balance Due</span>
                <span className="text-lg text-indigo-700">{fmt(invoice.balance_due)}</span>
              </div>
            </div>

            {/* Due date */}
            {invoice.due_date && (
              <p className="mt-3 text-xs text-slate-400">
                Due {new Date(invoice.due_date).toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' })}
              </p>
            )}
          </div>

          {/* Payment Form */}
          <div className="rounded-xl border border-slate-200 bg-white p-6">
            <h3 className="mb-4 text-base font-semibold text-slate-900">Pay with Card</h3>

            {errorMessage && (
              <div className="mb-4 rounded-lg bg-red-50 px-4 py-3 text-sm text-red-700">
                {errorMessage}
              </div>
            )}

            {/* Stripe card element mount point */}
            <div className="mb-4">
              <label className="mb-1 block text-sm font-medium text-slate-700">
                Card Details
              </label>
              <div
                ref={cardMountRef}
                className="rounded-lg border border-slate-200 px-4 py-3 focus-within:border-indigo-400 focus-within:ring-1 focus-within:ring-indigo-400"
                style={{ minHeight: '44px' }}
              />
              {cardError && (
                <p className="mt-1 text-xs text-red-600">{cardError}</p>
              )}
            </div>

            <button
              type="button"
              onClick={handlePay}
              disabled={isProcessing || !!cardError}
              className="w-full rounded-lg bg-indigo-600 py-3 text-sm font-semibold text-white hover:bg-indigo-700 disabled:opacity-50"
            >
              {isProcessing ? (
                <span className="flex items-center justify-center gap-2">
                  <span className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
                  Processing…
                </span>
              ) : (
                `Pay ${fmt(invoice.balance_due)}`
              )}
            </button>

            <div className="mt-4 flex items-center justify-center gap-1.5 text-xs text-slate-400">
              <svg className="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
              </svg>
              Payments are secured by Stripe
            </div>

            {invoice.terms && (
              <p className="mt-4 text-xs text-slate-400">
                <span className="font-medium">Terms: </span>{invoice.terms}
              </p>
            )}
          </div>
        </div>
      )}
    </PublicShell>
  );
}

// ── Shell layout for public pages ─────────────────────────────────────────────

function PublicShell({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-slate-50">
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex h-14 max-w-4xl items-center gap-3 px-4">
          <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-amber-500">
            <svg className="h-4 w-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round"
                d="M2.25 21h19.5m-18-18v18m10.5-18v18m6-13.5V21M6.75 6.75h.75m-.75 3h.75m-.75 3h.75m3-6h.75m-.75 3h.75m-.75 3h.75M6.75 21v-3.375c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125V21" />
            </svg>
          </div>
          <span className="text-sm font-semibold text-slate-800">BuilderStream</span>
          <span className="ml-auto text-xs text-slate-400">Secure Invoice Payment</span>
        </div>
      </header>
      <main className="mx-auto max-w-4xl px-4 py-8">
        {children}
      </main>
    </div>
  );
}
