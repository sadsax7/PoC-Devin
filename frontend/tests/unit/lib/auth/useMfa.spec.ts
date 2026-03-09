/**
 * @fileoverview Tests for the useMfa hook utility functions.
 *
 * Tests the pure helper functions exported by the useMfa hook.
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
import { extractAttemptsRemaining, mapMfaError } from '../../../../src/lib/auth/useMfa';
import type { ApiError } from '../../../../src/lib/api/client';

describe('useMfa utilities', () => {
  afterEach(() => sinon.restore());

  // ---------------------------------------------------------------
  // extractAttemptsRemaining
  // ---------------------------------------------------------------
  describe('extractAttemptsRemaining', () => {
    function makeErrWithDetail(status: number, detail: unknown): ApiError {
      return { status, message: 'err', detail };
    }

    // 1. Positive
    describe('Positive cases', () => {
      it('should_return_number_when_detail_contains_attempts_remaining', () => {
        // Arrange
        const err = makeErrWithDetail(401, { detail: '2 attempts remaining' });

        // Act
        const result = extractAttemptsRemaining(err);

        // Assert
        expect(result).to.equal(2);
      });

      it('should_return_zero_when_zero_attempts_remaining', () => {
        const err = makeErrWithDetail(401, { detail: '0 attempts remaining' });
        expect(extractAttemptsRemaining(err)).to.equal(0);
      });

      it('should_handle_case_insensitive_matching', () => {
        const err = makeErrWithDetail(401, { detail: '1 Attempts Remaining' });
        expect(extractAttemptsRemaining(err)).to.equal(1);
      });
    });

    // 2. Negative
    describe('Negative cases', () => {
      it('should_return_null_when_detail_has_no_attempts', () => {
        const err = makeErrWithDetail(401, { detail: 'Token expired' });
        expect(extractAttemptsRemaining(err)).to.be.null;
      });

      it('should_return_null_when_detail_is_undefined', () => {
        const err = makeErrWithDetail(401, undefined);
        expect(extractAttemptsRemaining(err)).to.be.null;
      });

      it('should_return_null_when_detail_is_empty_string', () => {
        const err = makeErrWithDetail(401, { detail: '' });
        expect(extractAttemptsRemaining(err)).to.be.null;
      });
    });

    // 3. Edge cases
    describe('Edge cases', () => {
      it('should_handle_flat_string_detail', () => {
        const err = makeErrWithDetail(401, '3 attempts remaining');
        expect(extractAttemptsRemaining(err)).to.equal(3);
      });

      it('should_handle_nested_detail_object', () => {
        const err = makeErrWithDetail(401, { detail: 'Invalid MFA code, 1 attempts remaining' });
        expect(extractAttemptsRemaining(err)).to.equal(1);
      });
    });
  });

  // ---------------------------------------------------------------
  // mapMfaError
  // ---------------------------------------------------------------
  describe('mapMfaError', () => {
    function makeErr(status: number, detail?: unknown): ApiError {
      return { status, message: 'err', detail };
    }

    // 1. Positive
    describe('Positive cases', () => {
      it('should_return_too_many_message_for_429', () => {
        const result = mapMfaError(makeErr(429));
        expect(result.message).to.contain('Demasiados intentos');
        expect(result.isTooMany).to.be.true;
      });

      it('should_return_invalid_code_message_when_attempts_remaining', () => {
        const result = mapMfaError(makeErr(401, { detail: '2 attempts remaining' }));
        expect(result.message).to.contain('Código incorrecto');
        expect(result.remaining).to.equal(2);
      });

      it('should_return_session_expired_message_when_no_attempts', () => {
        const result = mapMfaError(makeErr(401, { detail: 'Token expired' }));
        expect(result.message).to.contain('expirada');
        expect(result.isExpired).to.be.true;
      });
    });

    // 2. Negative
    describe('Negative cases', () => {
      it('should_return_server_error_for_500', () => {
        const result = mapMfaError(makeErr(500));
        expect(result.message).to.contain('servidor');
        expect(result.isTooMany).to.be.false;
        expect(result.isExpired).to.be.false;
      });

      it('should_return_server_error_for_unknown_status', () => {
        const result = mapMfaError(makeErr(418));
        expect(result.message).to.be.a('string');
        expect(result.message.length).to.be.greaterThan(5);
      });
    });

    // 3. Edge cases
    describe('Edge cases', () => {
      it('should_have_zero_remaining_for_429', () => {
        const result = mapMfaError(makeErr(429));
        expect(result.remaining).to.equal(0);
      });

      it('should_have_false_isExpired_for_429', () => {
        const result = mapMfaError(makeErr(429));
        expect(result.isExpired).to.be.false;
      });

      it('should_have_false_isTooMany_for_expired_401', () => {
        const result = mapMfaError(makeErr(401));
        expect(result.isTooMany).to.be.false;
      });
    });

    // 4. Interaction
    describe('Interaction cases', () => {
      it('should_not_throw_on_any_status', () => {
        [400, 401, 403, 429, 500, 503].forEach((code) => {
          expect(() => mapMfaError(makeErr(code))).to.not.throw();
        });
      });
    });

    // 5. State transitions
    describe('State transition cases', () => {
      it('should_differentiate_between_429_and_401_behaviors', () => {
        const tooMany = mapMfaError(makeErr(429));
        const expired = mapMfaError(makeErr(401));
        expect(tooMany.isTooMany).to.be.true;
        expect(expired.isTooMany).to.be.false;
      });

      it('should_differentiate_between_expired_and_wrong_code_401', () => {
        const expired = mapMfaError(makeErr(401));
        const wrongCode = mapMfaError(makeErr(401, { detail: '2 attempts remaining' }));
        expect(expired.isExpired).to.be.true;
        expect(wrongCode.isExpired).to.be.false;
      });
    });

    // 6. Accessibility
    describe('Accessibility cases', () => {
      it('should_return_human_readable_messages_for_all_statuses', () => {
        [401, 429, 500].forEach((code) => {
          const result = mapMfaError(makeErr(code));
          expect(result.message).to.be.a('string');
          expect(result.message.length).to.be.greaterThan(5);
        });
      });
    });

    // 7. Props variations
    describe('Props variations', () => {
      it('should_include_attempt_count_in_message_when_remaining_2', () => {
        const result = mapMfaError(makeErr(401, { detail: '2 attempts remaining' }));
        expect(result.message).to.contain('2');
      });

      it('should_include_attempt_count_in_message_when_remaining_1', () => {
        const result = mapMfaError(makeErr(401, { detail: '1 attempts remaining' }));
        expect(result.message).to.contain('1');
      });
    });
  });
});
