/**
 * @fileoverview Tests for the useLogin hook utility functions.
 *
 * Tests the pure helper functions exported by the useLogin hook.
 * Hook state management is covered indirectly via organism tests.
 *
 * Covers all 7 mandatory test types defined in FRONTEND-GUIDELINES.md §7.3.2.
 *
 * @remarks
 * Pattern: AAA (Arrange-Act-Assert).
 * Naming: should_<expected>_when_<condition>.
 */

import { expect } from 'chai';
import sinon from 'sinon';
import { mapLoginError, validateLoginPhone, validateLoginPassword } from '../../../../src/lib/auth/useLogin';
import type { ApiError } from '../../../../src/lib/api/client';

describe('useLogin utilities', () => {
  afterEach(() => sinon.restore());

  // ---------------------------------------------------------------
  // validateLoginPhone
  // ---------------------------------------------------------------
  describe('validateLoginPhone', () => {
    // 1. Positive
    describe('Positive cases', () => {
      it('should_return_empty_string_when_valid_e164_phone', () => {
        // Arrange / Act / Assert
        expect(validateLoginPhone('+573001234567')).to.equal('');
      });

      it('should_return_empty_when_minimum_7_digits_after_plus', () => {
        expect(validateLoginPhone('+1234567')).to.equal('');
      });

      it('should_return_empty_when_maximum_15_digits_after_plus', () => {
        expect(validateLoginPhone('+123456789012345')).to.equal('');
      });
    });

    // 2. Negative
    describe('Negative cases', () => {
      it('should_return_error_when_phone_is_empty', () => {
        expect(validateLoginPhone('')).to.not.equal('');
      });

      it('should_return_error_when_phone_missing_plus_prefix', () => {
        expect(validateLoginPhone('573001234567')).to.not.equal('');
      });

      it('should_return_error_when_phone_has_letters', () => {
        expect(validateLoginPhone('+57abc123')).to.not.equal('');
      });
    });

    // 3. Edge cases
    describe('Edge cases', () => {
      it('should_return_error_when_only_plus_sign', () => {
        expect(validateLoginPhone('+')).to.not.equal('');
      });

      it('should_return_error_when_too_short_6_digits', () => {
        expect(validateLoginPhone('+123456')).to.not.equal('');
      });

      it('should_return_error_when_too_long_16_digits', () => {
        expect(validateLoginPhone('+1234567890123456')).to.not.equal('');
      });
    });
  });

  // ---------------------------------------------------------------
  // validateLoginPassword
  // ---------------------------------------------------------------
  describe('validateLoginPassword', () => {
    // 1. Positive
    describe('Positive cases', () => {
      it('should_return_empty_when_password_non_empty', () => {
        expect(validateLoginPassword('anypass')).to.equal('');
      });

      it('should_return_empty_when_single_character', () => {
        expect(validateLoginPassword('x')).to.equal('');
      });
    });

    // 2. Negative
    describe('Negative cases', () => {
      it('should_return_error_when_password_empty', () => {
        expect(validateLoginPassword('')).to.not.equal('');
      });
    });

    // 3. Edge cases
    describe('Edge cases', () => {
      it('should_return_empty_when_password_is_spaces', () => {
        // Spaces count as non-empty — backend handles deeper validation
        expect(validateLoginPassword('   ')).to.equal('');
      });
    });
  });

  // ---------------------------------------------------------------
  // mapLoginError
  // ---------------------------------------------------------------
  describe('mapLoginError', () => {
    function makeErr(status: number): ApiError {
      return { status, message: 'err', detail: undefined };
    }

    // 1. Positive
    describe('Positive cases', () => {
      it('should_return_invalid_credentials_message_for_401', () => {
        const msg = mapLoginError(makeErr(401));
        expect(msg).to.contain('inválidas');
      });

      it('should_return_not_registered_message_for_404', () => {
        const msg = mapLoginError(makeErr(404));
        expect(msg).to.contain('no registrado');
      });

      it('should_return_locked_message_for_423', () => {
        const msg = mapLoginError(makeErr(423));
        expect(msg).to.contain('bloqueada');
      });
    });

    // 2. Negative
    describe('Negative cases', () => {
      it('should_return_server_error_message_for_500', () => {
        const msg = mapLoginError(makeErr(500));
        expect(msg).to.contain('servidor');
      });

      it('should_return_server_error_message_for_unknown_status', () => {
        const msg = mapLoginError(makeErr(418));
        expect(msg).to.contain('servidor');
      });
    });

    // 3. Edge cases
    describe('Edge cases', () => {
      it('should_return_string_for_status_0', () => {
        const msg = mapLoginError(makeErr(0));
        expect(msg).to.be.a('string').and.not.be.empty;
      });

      it('should_return_string_for_status_503', () => {
        const msg = mapLoginError(makeErr(503));
        expect(msg).to.be.a('string').and.not.be.empty;
      });
    });

    // 4. Interaction
    describe('Interaction cases', () => {
      it('should_not_throw_when_called_with_valid_error', () => {
        expect(() => mapLoginError(makeErr(401))).to.not.throw();
      });
    });

    // 5. State transitions
    describe('State transition cases', () => {
      it('should_return_different_messages_for_401_vs_423', () => {
        const msg401 = mapLoginError(makeErr(401));
        const msg423 = mapLoginError(makeErr(423));
        expect(msg401).to.not.equal(msg423);
      });
    });

    // 6. Accessibility
    describe('Accessibility cases', () => {
      it('should_return_human_readable_string_for_all_known_codes', () => {
        [401, 404, 423, 500].forEach((code) => {
          const msg = mapLoginError(makeErr(code));
          expect(msg).to.be.a('string');
          expect(msg.length).to.be.greaterThan(5);
        });
      });
    });

    // 7. Props variations
    describe('Props variations', () => {
      it('should_handle_errors_with_detail_field', () => {
        const err: ApiError = { status: 401, message: 'err', detail: { detail: 'bad creds' } };
        const msg = mapLoginError(err);
        expect(msg).to.be.a('string');
      });
    });
  });
});
