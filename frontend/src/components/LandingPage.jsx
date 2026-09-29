import React from 'react';
import { ArrowDown, ArrowRight, Activity, Layers3, MapPinned, ShieldAlert } from 'lucide-react';

const features = [
  { number: '01', title: 'Nearby well intelligence', text: 'Explore offset wells within a selected radius.', icon: MapPinned },
  { number: '02', title: 'Historical drilling knowledge', text: 'Review previous incidents, causes and recorded mitigation.', icon: Layers3 },
  { number: '03', title: 'Live telemetry context', text: 'Monitor current drilling parameters alongside well history.', icon: Activity },
  { number: '04', title: 'Risk intelligence', text: 'Compare current conditions with historical offset behaviour.', icon: ShieldAlert },
];

const flow = ['Current well', 'Nearby wells', 'Historical knowledge', 'Current telemetry', 'Risk intelligence', 'Decision support'];

export default function LandingPage({ onEnter }) {
  return (
    <div className="nwis-landing">
      <header className="nwis-landing-header">
        <a className="nwis-landing-brand" href="#top" aria-label="NWIS home">
          <span className="nwis-brand-mark">NWIS</span>
          <span><strong>NWIS</strong><small>Drilling intelligence platform</small></span>
        </a>
        <a className="nwis-about-link" href="#platform">About the platform <ArrowDown size={14} /></a>
      </header>

      <main id="top">
        <section className="nwis-landing-hero">
          <div className="nwis-hero-copy">
            <div className="nwis-landing-eyebrow"><span /> SMI / DRILLING INTELLIGENCE PLATFORM</div>
            <h1>Nearby Wells<br /><em>Intelligence System</em></h1>
            <p className="nwis-hero-lede">Turn historical offset-well knowledge into actionable drilling intelligence.</p>
            <p className="nwis-hero-description">NWIS connects nearby wells, historical drilling events, formation information and current telemetry to help drilling teams identify potential risks before they become operational problems.</p>
            <div className="nwis-hero-actions">
              <button type="button" className="nwis-enter-button" onClick={onEnter}>Enter NWIS <ArrowRight size={17} /></button>
              <a className="nwis-explore-link" href="#platform">Explore the platform</a>
            </div>
            <div className="nwis-hero-footnote"><span /> Operational decision support · Synthetic demonstration data</div>
          </div>

          <div className="nwis-geo-visual" aria-label="Illustration showing a current well, geological layers, nearby offset wells and historical risk intelligence" role="img">
            <div className="nwis-visual-topline"><span>SUBSURFACE CONTEXT</span><span>FIELD VIEW / 01</span></div>
            <div className="nwis-layer-label nwis-layer-a">FORMATION A <small>SHALLOW INTERVAL</small></div>
            <div className="nwis-layer-label nwis-layer-b">FORMATION B <small>OFFSET EVENT ZONE</small></div>
            <div className="nwis-layer-label nwis-layer-c">FORMATION C <small>DEEPER INTERVAL</small></div>
            <div className="nwis-surface-line"><span>GROUND LEVEL</span></div>
            <div className="nwis-wellbore nwis-active-bore"><span className="nwis-bore-head">ACTIVE</span><span className="nwis-bore-line" /><span className="nwis-bit" /></div>
            <div className="nwis-wellbore nwis-offset-bore nwis-offset-one"><span className="nwis-offset-dot" /><span className="nwis-offset-line" /></div>
            <div className="nwis-wellbore nwis-offset-bore nwis-offset-two"><span className="nwis-offset-dot" /><span className="nwis-offset-line" /></div>
            <div className="nwis-event-marker"><span /> HISTORICAL EVENT</div>
            <div className="nwis-risk-callout"><i /> OFFSET RISK INTERVAL <b>2,900–3,040 m</b></div>
            <div className="nwis-visual-caption"><span className="nwis-caption-rule" /> OFFSET WELL KNOWLEDGE <ArrowRight size={13} /> ACTIONABLE CONTEXT</div>
            <div className="nwis-visual-coordinates">26° N&nbsp;&nbsp; 94° E <span>DEPTH / m</span></div>
          </div>
        </section>

        <section className="nwis-feature-section" id="platform">
          <div className="nwis-section-heading"><span>ONE CONNECTED WORKSPACE</span><h2>Operational context, brought together.</h2></div>
          <div className="nwis-feature-grid">
            {features.map(({ number, title, text, icon: Icon }) => (
              <article className="nwis-feature" key={number}>
                <div className="nwis-feature-top"><span>{number}</span><Icon size={19} strokeWidth={1.7} /></div>
                <h3>{title}</h3><p>{text}</p>
              </article>
            ))}
          </div>
        </section>

        <section className="nwis-how-section">
          <div className="nwis-section-heading"><span>THE NWIS WORKFLOW</span><h2>From well context to decision support.</h2></div>
          <div className="nwis-flow" aria-label={flow.join(' then ')}>
            {flow.map((item, index) => (
              <React.Fragment key={item}>
                <div className={`nwis-flow-step ${index === flow.length - 1 ? 'is-final' : ''}`}><span>{String(index + 1).padStart(2, '0')}</span><strong>{item}</strong></div>
                {index < flow.length - 1 && <ArrowRight className="nwis-flow-arrow" size={16} aria-hidden="true" />}
              </React.Fragment>
            ))}
          </div>
        </section>

        <section className="nwis-landing-cta">
          <div><span>READY TO EXPLORE DRILLING INTELLIGENCE?</span><h2>Bring the full well picture into view.</h2></div>
          <button type="button" className="nwis-enter-button" onClick={onEnter}>Enter NWIS <ArrowRight size={17} /></button>
        </section>
      </main>
      <footer className="nwis-landing-footer"><span>NWIS · Nearby Wells Intelligence System</span><span>Oil India Limited SIH Prototype · Synthetic demonstration data</span></footer>
    </div>
  );
}
