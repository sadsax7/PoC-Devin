/**
 * @fileoverview Tests for the RegisterForm organism — validation helpers.
 *
 * Tests the pure validation functions exported from RegisterForm.
 * Covers all 7 mandatory test types defined in FRONTEND-GUIDELINES.md §7.3.2.
 *
 * @remarks
 * Pattern: AAA (Arrange-Act-Assert).
 * Naming: should_<expected>_when_<condition>.
 */

import { expect } from 'chai';
import {
  validatePhone,
  validatePassword,
  validateConfirmPassword,
  validateEmail,
  validateName,
} from '../../../src/components/organisms/RegisterForm';

// =============================================================
// validatePhone
// =============================================================
describe('validatePhone', () => {
  describe('Positive cases', () => {
    it('should_return_empty_when_valid_e164_phone', () => {
      expect(validatePhone('+573001234567')).to.equal('');
    });

    it('should_accept_minimum_length_e164', () => {
      // +1234567 is 7 digits after +
      expect(validatePhone('+1234567')).to.equal('');
    });

    it('should_accept_maximum_length_e164', () => {
      // 15 digits after +
      expect(validatePhone('+123456789012345')).to.equal('');
    });
  });

  describe('Negative cases', () => {
    it('should_return_error_when_empty', () => {
      expect(validatePhone('')).to.equal('El teléfono es obligatorio.');
    });

    it('should_return_error_when_missing_plus', () => {
      expect(validatePhone('573001234567')).to.contain('Formato de teléfono inválido');
    });

    it('should_return_error_when_contains_letters', () => {
      expect(validatePhone('+57abc1234567')).to.contain('Formato de teléfono inválido');
    });

    it('should_return_error_when_contains_spaces', () => {
      expect(validatePhone('+57 300 1234567')).to.contain('Formato de teléfono inválido');
    });
  });

  describe('Edge cases', () => {
    it('should_return_error_when_too_short', () => {
      // Only 6 digits after +
      expect(validatePhone('+123456')).to.contain('Formato de teléfono inválido');
    });

    it('should_return_error_when_too_long', () => {
      // 16 digits after +
      expect(validatePhone('+1234567890123456')).to.contain('Formato de teléfono inválido');
    });

    it('should_return_error_when_only_plus', () => {
      expect(validatePhone('+')).to.contain('Formato de teléfono inválido');
    });
  });
});

// =============================================================
// validatePassword
// =============================================================
describe('validatePassword', () => {
  describe('Positive cases', () => {
    it('should_return_empty_when_all_rules_met', () => {
      expect(validatePassword('Abcdef1!')).to.equal('');
    });

    it('should_accept_exactly_8_characters', () => {
      expect(validatePassword('Abcde1!x')).to.equal('');
    });

    it('should_accept_128_characters', () => {
      const pw = 'Aa1!' + 'x'.repeat(124);
      expect(validatePassword(pw)).to.equal('');
    });
  });

  describe('Negative cases', () => {
    it('should_return_error_when_empty', () => {
      expect(validatePassword('')).to.equal('La contraseña es obligatoria.');
    });

    it('should_return_error_when_too_short', () => {
      expect(validatePassword('Ab1!')).to.equal('Mínimo 8 caracteres.');
    });

    it('should_return_error_when_too_long', () => {
      const pw = 'Aa1!' + 'x'.repeat(125);
      expect(validatePassword(pw)).to.equal('Máximo 128 caracteres.');
    });

    it('should_return_error_when_no_uppercase', () => {
      expect(validatePassword('abcdef1!')).to.equal('Debe contener al menos 1 mayúscula.');
    });

    it('should_return_error_when_no_lowercase', () => {
      expect(validatePassword('ABCDEF1!')).to.equal('Debe contener al menos 1 minúscula.');
    });

    it('should_return_error_when_no_digit', () => {
      expect(validatePassword('Abcdefg!')).to.equal('Debe contener al menos 1 número.');
    });

    it('should_return_error_when_no_special', () => {
      expect(validatePassword('Abcdefg1')).to.equal(
        'Debe contener al menos 1 carácter especial.',
      );
    });
  });

  describe('Edge cases', () => {
    it('should_return_error_when_exactly_7_characters', () => {
      expect(validatePassword('Abc1!xx')).to.equal('Mínimo 8 caracteres.');
    });

    it('should_check_rules_in_order_length_first', () => {
      // Short + no uppercase — length error comes first
      expect(validatePassword('a1!')).to.equal('Mínimo 8 caracteres.');
    });
  });
});

// =============================================================
// validateConfirmPassword
// =============================================================
describe('validateConfirmPassword', () => {
  describe('Positive cases', () => {
    it('should_return_empty_when_passwords_match', () => {
      expect(validateConfirmPassword('Abcdef1!', 'Abcdef1!')).to.equal('');
    });
  });

  describe('Negative cases', () => {
    it('should_return_error_when_empty_confirm', () => {
      expect(validateConfirmPassword('Abcdef1!', '')).to.equal('Confirma tu contraseña.');
    });

    it('should_return_error_when_mismatch', () => {
      expect(validateConfirmPassword('Abcdef1!', 'Different1!')).to.equal(
        'Las contraseñas no coinciden',
      );
    });
  });

  describe('Edge cases', () => {
    it('should_be_case_sensitive', () => {
      expect(validateConfirmPassword('Abcdef1!', 'abcdef1!')).to.equal(
        'Las contraseñas no coinciden',
      );
    });

    it('should_match_when_both_empty_but_empty_triggers_required', () => {
      // Both empty → confirm is empty → "Confirma tu contraseña."
      expect(validateConfirmPassword('', '')).to.equal('Confirma tu contraseña.');
    });
  });
});

// =============================================================
// validateEmail
// =============================================================
describe('validateEmail', () => {
  describe('Positive cases', () => {
    it('should_return_empty_when_valid_email', () => {
      expect(validateEmail('user@example.com')).to.equal('');
    });

    it('should_return_empty_when_email_is_empty_optional', () => {
      expect(validateEmail('')).to.equal('');
    });
  });

  describe('Negative cases', () => {
    it('should_return_error_when_missing_at', () => {
      expect(validateEmail('userexample.com')).to.equal('Formato de email inválido.');
    });

    it('should_return_error_when_missing_domain', () => {
      expect(validateEmail('user@')).to.equal('Formato de email inválido.');
    });

    it('should_return_error_when_missing_tld', () => {
      expect(validateEmail('user@example')).to.equal('Formato de email inválido.');
    });

    it('should_return_error_when_contains_spaces', () => {
      expect(validateEmail('user @example.com')).to.equal('Formato de email inválido.');
    });
  });

  describe('Edge cases', () => {
    it('should_return_error_when_exceeds_255_characters', () => {
      const long = 'a'.repeat(250) + '@b.com';
      expect(validateEmail(long)).to.equal('Máximo 255 caracteres.');
    });

    it('should_accept_email_with_subdomain', () => {
      expect(validateEmail('user@sub.example.com')).to.equal('');
    });

    it('should_accept_email_with_plus_sign', () => {
      expect(validateEmail('user+tag@example.com')).to.equal('');
    });
  });
});

// =============================================================
// validateName
// =============================================================
describe('validateName', () => {
  describe('Positive cases', () => {
    it('should_return_empty_when_valid_name', () => {
      expect(validateName('Juan Pérez')).to.equal('');
    });

    it('should_return_empty_when_name_is_empty_optional', () => {
      expect(validateName('')).to.equal('');
    });

    it('should_accept_exactly_100_characters', () => {
      expect(validateName('A'.repeat(100))).to.equal('');
    });
  });

  describe('Negative cases', () => {
    it('should_return_error_when_exceeds_100_characters', () => {
      expect(validateName('A'.repeat(101))).to.equal('Máximo 100 caracteres.');
    });
  });

  describe('Edge cases', () => {
    it('should_accept_name_with_special_characters', () => {
      expect(validateName("O'Brien-Smith")).to.equal('');
    });

    it('should_accept_name_with_unicode', () => {
      expect(validateName('José María Ñoño')).to.equal('');
    });
  });
});
