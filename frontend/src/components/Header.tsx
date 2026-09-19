import { useState } from "react";

import type { ConnectionState } from "../api/client";
import { CompassIcon } from "./icons";

/**
 * Application header.
 *
 * Brand mark and product name on the left, the organisation being advised and
 * a compact service status on the right.
 *
 * **The status is truthful about what it knows.** "Ready" means the backend
 * answered and local configuration looks usable. It does not mean the
 * credentials work, which only a completed request establishes, so the detail
 * panel says so rather than letting a green dot imply it.
 *
 * Version and build stage stay available behind a disclosure. They are useful
 * to whoever is debugging and meaningless to a manager, so they are one click
 * away rather than in the most prominent corner of the page.
 */
export default function Header({
  connection,
  organisation,
}: {
  connection: ConnectionState;
  organisation: string | null;
}) {
  const [open, setOpen] = useState(false);

  const status =
    connection.kind === "checking"
      ? { tone: "idle", label: "Checking…" }
      : connection.kind === "failed"
        ? { tone: "bad", label: "Not connected" }
        : connection.health.model_configured_locally
          ? { tone: "good", label: "Ready" }
          : { tone: "bad", label: "Not configured" };

  return (
    <header className="masthead">
      <div className="masthead__inner">
        <div className="brand">
          <span className="brand__mark" aria-hidden="true">
            <CompassIcon size={17} />
          </span>
          <span className="brand__name">AI Initiative Advisor</span>
        </div>

        <div className="masthead__right">
          {organisation && <span className="masthead__org">{organisation}</span>}

          <div className="service">
            <button
              type="button"
              className={`service__chip service__chip--${status.tone}`}
              aria-expanded={open}
              onClick={() => setOpen((v) => !v)}
            >
              <span className="service__dot" aria-hidden="true" />
              {status.label}
              <span className="visually-hidden"> — service details</span>
            </button>

            {open && (
              <div className="service__panel" role="region" aria-label="Service details">
                {connection.kind === "connected" ? (
                  <>
                    <p className="service__row">
                      <span className="service__key">Version</span>
                      <span>{connection.health.version}</span>
                    </p>
                    <p className="service__row">
                      <span className="service__key">Stage</span>
                      <span>{connection.health.stage}</span>
                    </p>
                    <p className="service__row">
                      <span className="service__key">Model</span>
                      <span>
                        {connection.health.model_configured_locally
                          ? "configured"
                          : "not configured"}
                      </span>
                    </p>
                    {connection.health.configuration_problems.length > 0 && (
                      <ul className="service__problems">
                        {connection.health.configuration_problems.map((problem, i) => (
                          <li key={i}>{problem}</li>
                        ))}
                      </ul>
                    )}
                    <p className="service__note">{connection.health.configuration_note}</p>
                  </>
                ) : connection.kind === "failed" ? (
                  <p className="service__note">
                    The advisor service is not responding. Start it with <code>npm run dev</code>.
                  </p>
                ) : (
                  <p className="service__note">Checking the service…</p>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </header>
  );
}
