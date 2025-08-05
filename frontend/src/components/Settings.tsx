import React, { useState, useEffect } from 'react';

// Add index signature to allow string keys
interface SettingsState {
  [key: string]: string | number | boolean;
  gemini_api_key: string;
  gemini_model_name: string;
  gemini_max_tokens: number;
  gemini_temperature: number;
  local_model_name: string;
  local_max_tokens: number;
  local_temperature: number;
  secure_config: boolean;
  encrypt_sensitive_data: boolean;
  prompt_style: string;
  notification_level: string;
  log_level: string;
  log_file: string;
  temp_dir: string;
  backup_dir: string;
  config_backup: boolean;
  auto_update: boolean;
  telemetry: boolean;
  experimental_features: boolean;
  custom_plugins: string;
  api_endpoint: string;
  timeout_settings: string;
}

const initialSettings: SettingsState = {
  gemini_api_key: '',
  gemini_model_name: 'gemini-2.5-flash-l…',
  gemini_max_tokens: 2048,
  gemini_temperature: 0.7,
  local_model_name: 'google/gemma-1.1-3…',
  local_max_tokens: 1024,
  local_temperature: 0.7,
  secure_config: true,
  encrypt_sensitive_data: false,
  prompt_style: 'simple',
  notification_level: 'info',
  log_level: 'INFO',
  log_file: '~/.overseer/overs…',
  temp_dir: '/tmp/overseer',
  backup_dir: '~/.overseer/backu…',
  config_backup: false,
  auto_update: false,
  telemetry: false,
  experimental_features: false,
  custom_plugins: '',
  api_endpoint: '',
  timeout_settings: '30,60,120',
  notifications_on: true,
};

const settingsTabs = [
  {
    category: 'LLM Configuration',
    settings: [
      // Gemini
      { key: 'gemini_api_key', type: 'string', label: 'Gemini API Key', desc: 'Your Gemini API key for online LLM access' },
      { key: 'gemini_model_name', type: 'string', label: 'Gemini Model Name', desc: 'Specific Gemini model to use' },
      { key: 'gemini_max_tokens', type: 'int', label: 'Gemini Max Tokens', desc: 'Maximum tokens for Gemini responses' },
      { key: 'gemini_temperature', type: 'float', label: 'Gemini Temperature', desc: 'Controls response creativity (higher = more creative)' },
      // Local Model
      { key: 'local_model_name', type: 'string', label: 'Local Model Name', desc: 'Local model to use for inference' },
      { key: 'local_max_tokens', type: 'int', label: 'Local Max Tokens', desc: 'Maximum tokens for local model responses' },
      { key: 'local_temperature', type: 'float', label: 'Local Temperature', desc: 'Controls local model response creativity' },
    ]
  },
  {
    category: 'Security Settings',
    settings: [
      { key: 'secure_config', type: 'bool', label: 'Secure Config', desc: 'Enable secure configuration mode' },
      { key: 'encrypt_sensitive_data', type: 'bool', label: 'Encrypt Sensitive Data', desc: 'Encrypt sensitive configuration data' },
    ]
  },
  {
    category: 'UI Settings',
    settings: [
      { key: 'prompt_style', type: 'string', label: 'Prompt Style', desc: 'Command prompt style' },
      { key: 'notifications_on', type: 'bool', label: 'Notifications', desc: 'Enable notifications' },
    ]
  },
  {
    category: 'Advanced Settings',
    settings: [
      { key: 'log_level', type: 'string', label: 'Log Level', desc: 'Logging level' },
      { key: 'log_file', type: 'string', label: 'Log File', desc: 'Path to log file' },
      { key: 'temp_dir', type: 'string', label: 'Temp Dir', desc: 'Directory for temporary files' },
      { key: 'backup_dir', type: 'string', label: 'Backup Dir', desc: 'Directory for file backups' },
      { key: 'config_backup', type: 'bool', label: 'Config Backup', desc: 'Automatically backup configuration' },
      { key: 'auto_update', type: 'bool', label: 'Auto Update', desc: 'Automatically check for updates' },
      { key: 'telemetry', type: 'bool', label: 'Telemetry', desc: 'Enable usage telemetry' },
      { key: 'experimental_features', type: 'bool', label: 'Experimental Features', desc: 'Enable experimental features' },
      { key: 'custom_plugins', type: 'string', label: 'Custom Plugins', desc: 'Custom plugin directories (comma separated)' },
      { key: 'api_endpoint', type: 'string', label: 'API Endpoint', desc: 'Custom API endpoint' },
      { key: 'timeout_settings', type: 'string', label: 'Timeout Settings', desc: 'Timeout settings (connect,read,write)' },
    ]
  },
];

const Settings: React.FC = () => {
  const [settings, setSettings] = useState<SettingsState>(initialSettings);
  const [activeTab, setActiveTab] = useState(0);

  const handleChange = (key: string, value: any) => {
    setSettings(prev => ({ ...prev, [key]: value }));
  };

  useEffect(() => {
    // Inject global scrollbar CSS for all components
    const style = document.createElement('style');
    style.innerHTML = `
      /* Reduce scrollbar width globally */
      ::-webkit-scrollbar {
        width: 7px;
        height: 7px;
      }
      ::-webkit-scrollbar-thumb {
        background: #2e4a36;
        border-radius: 6px;
      }
      ::-webkit-scrollbar-track {
        background: #16281a;
      }
      html {
        scrollbar-width: thin;
        scrollbar-color: #2e4a36 #16281a;
      }
    `;
    document.head.appendChild(style);
    return () => {
      document.head.removeChild(style);
    };
  }, []);
  return (
    <div className="card" style={{ maxWidth: 720, margin: '2em auto', textAlign: 'center', height: 'auto', minHeight: 0 }}>
      <style>{`
        input[type=number]::-webkit-inner-spin-button,
        input[type=number]::-webkit-outer-spin-button {
          -webkit-appearance: none;
          margin: 0;
        }
        input[type=number] {
          -moz-appearance: textfield;
        }
      `}</style>
      <h2 style={{ marginBottom: '1.5em' }}>Settings</h2>
      <div style={{ display: 'flex', gap: 8, marginBottom: 24, justifyContent: 'center', flexWrap: 'wrap' }}>
        {settingsTabs.map((section, idx) => (
          <button
            key={section.category}
            onClick={() => setActiveTab(idx)}
            style={{
              padding: '0.6em 1.4em',
              borderRadius: 8,
              border: 'none',
              background: idx === activeTab ? 'var(--accent-gradient, #4aff80)' : 'var(--accent-bg-light, #16281a)',
              color: idx === activeTab ? 'var(--text-color-dark, #101c14)' : 'var(--accent-color, #4aff80)',
              fontWeight: 600,
              fontSize: '1rem',
              cursor: 'pointer',
              boxShadow: idx === activeTab ? '0 2px 8px var(--accent-color-dark, #1e4023)33' : 'none',
              transition: 'background 0.2s, color 0.2s',
              outline: idx === activeTab ? '2px solid var(--accent-color)' : 'none',
              marginBottom: 0,
            }}
            aria-selected={idx === activeTab}
            tabIndex={0}
          >
            {section.category}
          </button>
        ))}
      </div>
      <div style={{ textAlign: 'left' }}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
          {settingsTabs[activeTab].settings.map(s => {
            if (s.key === 'timeout_settings') {
              // Parse the timeout_settings value into three fields
              const [connect, read, write] = (settings.timeout_settings as string).split(',');
              return (
                <div key={s.key} style={{ display: 'flex', alignItems: 'flex-start', marginBottom: 8, gap: 16 }}>
                  <label style={{ minWidth: 180, color: 'var(--accent-color)', fontWeight: 500, fontSize: '1rem', lineHeight: 1.2, marginTop: 2 }}>Timeout Settings</label>
                  <div style={{ flex: 1, display: 'flex', flexDirection: 'row', alignItems: 'flex-start', justifyContent: 'flex-end', gap: 12 }}>
                    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', width: 90 }}>
                      <input
                        type="number"
                        min={0}
                        value={connect || ''}
                        onChange={e => {
                          const vals = [e.target.value, read || '', write || ''];
                          handleChange('timeout_settings', vals.join(','));
                        }}
                        style={{ width: '100%', fontFamily: 'monospace', fontSize: '1rem', padding: '0.4em 0.7em', borderRadius: 6, border: '1.5px solid #4aff80', background: 'var(--accent-bg-light)', color: '#e6ffe6', marginBottom: 2, MozAppearance: 'textfield' }}
                        inputMode="numeric"
                        pattern="[0-9]*"
                        onWheel={e => e.currentTarget.blur()}
                      />
                      <span style={{ color: '#b6ffb6', fontSize: '0.7em', opacity: 0.8, lineHeight: 1.2, textAlign: 'right', alignSelf: 'flex-end' }}>connect</span>
                    </div>
                    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', width: 90 }}>
                      <input
                        type="number"
                        min={0}
                        value={read || ''}
                        onChange={e => {
                          const vals = [connect || '', e.target.value, write || ''];
                          handleChange('timeout_settings', vals.join(','));
                        }}         style={{ width: '100%', fontFamily: 'monospace', fontSize: '1rem', padding: '0.4em 0.7em', borderRadius: 6, border: '1.5px solid #4aff80', background: 'var(--accent-bg-light)', color: '#e6ffe6', marginBottom: 2, MozAppearance: 'textfield' }}
                        inputMode="numeric"
                        pattern="[0-9]*"
                        onWheel={e => e.currentTarget.blur()}
                      />
                      <span style={{ color: '#b6ffb6', fontSize: '0.7em', opacity: 0.8, lineHeight: 1.2, textAlign: 'right', alignSelf: 'flex-end' }}>read</span>
                    </div>
                    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', width: 90 }}>
                      <input
                        type="number"
                        min={0}
                        value={write || ''}
                        onChange={e => {
                          const vals = [connect || '', read || '', e.target.value];
                          handleChange('timeout_settings', vals.join(','));
                        }}
                        style={{ width: '100%', fontFamily: 'monospace', fontSize: '1rem', padding: '0.4em 0.7em', borderRadius: 6, border: '1.5px solid #4aff80', background: 'var(--accent-bg-light)', color: '#e6ffe6', marginBottom: 2, MozAppearance: 'textfield' }}
                        inputMode="numeric"
                        pattern="[0-9]*"
                        onWheel={e => e.currentTarget.blur()}
                      />
                      <span style={{ color: '#b6ffb6', fontSize: '0.7em', opacity: 0.8, lineHeight: 1.2, textAlign: 'right', alignSelf: 'flex-end' }}>write</span>
                    </div>
                  </div>
                </div>
              );
            }
            return (
              <div key={s.key} style={{ display: 'flex', alignItems: 'flex-start', marginBottom: 8, gap: 16 }}>
                <label htmlFor={s.key} style={{ minWidth: 180, color: 'var(--accent-color)', fontWeight: 500, fontSize: '1rem', lineHeight: 1.2, marginTop: 2 }}>{s.label}</label>
                <div style={{ flex: 1, display: 'flex', flexDirection: 'row', alignItems: 'flex-start', justifyContent: 'flex-end', position: 'relative' }}>
                  <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', width: '100%' }}>
                    {s.type === 'bool' ? (
                      <span style={{ display: 'inline-flex', alignItems: 'center', height: 22, marginBottom: 2, marginLeft: 0, marginRight: 0 }}>
                        <input
                          id={s.key}
                          type="checkbox"
                          checked={!!settings[s.key]}
                          onChange={e => handleChange(s.key, e.target.checked)}
                          style={{
                            width: 0,
                            height: 0,
                            opacity: 0,
                            position: 'absolute',
                          }}
                        />
                        <span
                          tabIndex={0}
                          role="checkbox"
                          aria-checked={!!settings[s.key]}
                          onClick={() => handleChange(s.key, !settings[s.key])}
                          onKeyDown={e => { if (e.key === ' ' || e.key === 'Enter') handleChange(s.key, !settings[s.key]); }}
                          style={{
                            display: 'inline-block',
                            width: 22,
                            height: 22,
                            borderRadius: 4,
                            border: '2px solid #4aff80',
                            background: !!settings[s.key] ? '#4aff80' : 'transparent',
                            boxSizing: 'border-box',
                            cursor: 'pointer',
                            transition: 'background 0.2s, border 0.2s',
                            outline: 'none',
                            verticalAlign: 'middle',
                            marginTop: 0,
                            marginBottom: 0,
                          }}
                        />
                      </span>
                    ) : (
                      <input
                        id={s.key}
                        type={s.type === 'int' ? 'number' : s.type === 'float' ? 'number' : 'text'}
                        step={s.type === 'float' ? '0.01' : undefined}
                        value={settings[s.key] as string | number}
                        onChange={e => handleChange(s.key, s.type === 'int' ? parseInt(e.target.value) : s.type === 'float' ? parseFloat(e.target.value) : e.target.value)}
                        style={{ width: '100%', minWidth: 180, fontFamily: 'monospace', fontSize: '1rem', padding: '0.4em 0.7em', borderRadius: 6, border: '1.5px solid #4aff80', background: 'var(--accent-bg-light)', color: '#e6ffe6', verticalAlign: 'baseline', marginBottom: 2, MozAppearance: 'textfield' }}
                        inputMode={s.type === 'int' || s.type === 'float' ? 'numeric' : undefined}
                        pattern={s.type === 'int' || s.type === 'float' ? '[0-9]*' : undefined}
                        onWheel={e => e.currentTarget.blur()}
                      />
                    )}
                    <span style={{ color: '#b6ffb6', fontSize: '0.7em', opacity: 0.8, lineHeight: 1.2, marginLeft: 0, maxWidth: '100%', wordBreak: 'break-word', whiteSpace: 'normal', textAlign: 'right', alignSelf: 'flex-end' }}>{s.desc}</span>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

export default Settings;
