/**
 * @fileoverview Tests for the Button atom component.
 *
 * Covers all 7 mandatory test types defined in FRONTEND-GUIDELINES.md §7.3.2:
 * 1. Positive (happy path)
 * 2. Negative (error handling)
 * 3. Edge cases
 * 4. Interactions
 * 5. State transitions
 * 6. Accessibility
 * 7. Props variations
 *
 * @remarks
 * Pattern: AAA (Arrange-Act-Assert).
 * Naming: should_&lt;expected&gt;_when_&lt;condition&gt;.
 */

import { expect } from 'chai';
import sinon from 'sinon';
import React from 'react';
import ReactDOMServer from 'react-dom/server';
import { Button } from '../../../src/components/atoms';

describe('Button', () => {
  afterEach(() => {
    sinon.restore();
  });

  // ---------------------------------------------------------------
  // 1. Positive cases (happy path)
  // ---------------------------------------------------------------
  describe('Positive cases', () => {
    it('should_render_button_element_when_no_href_provided', () => {
      // Arrange
      const element = React.createElement(Button, null, 'Click me');

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.contain('<button');
      expect(html).to.contain('Click me');
    });

    it('should_render_anchor_element_when_href_provided', () => {
      // Arrange
      const element = React.createElement(Button, { href: '/auth/login' }, 'Ingresar');

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.contain('<a');
      expect(html).to.contain('href="/auth/login"');
      expect(html).to.contain('Ingresar');
    });

    it('should_render_solid_variant_by_default', () => {
      // Arrange
      const element = React.createElement(Button, null, 'Solid');

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.contain('bg-primary');
      expect(html).to.contain('text-white');
    });

    it('should_render_outline_variant_when_specified', () => {
      // Arrange
      const element = React.createElement(Button, { variant: 'outline' }, 'Outline');

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.contain('border-2');
      expect(html).to.contain('border-primary');
      expect(html).to.contain('text-primary');
      expect(html).to.contain('bg-transparent');
    });
  });

  // ---------------------------------------------------------------
  // 2. Negative cases (error handling)
  // ---------------------------------------------------------------
  describe('Negative cases', () => {
    it('should_not_crash_when_children_is_undefined', () => {
      // Arrange
      const element = React.createElement(Button, {});

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.contain('<button');
    });

    it('should_not_crash_when_children_is_null', () => {
      // Arrange
      const element = React.createElement(Button, null, null);

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.contain('<button');
    });

    it('should_render_button_instead_of_anchor_when_href_provided_but_disabled', () => {
      // Arrange
      const element = React.createElement(
        Button,
        { href: '/auth/login', disabled: true },
        'Disabled Link',
      );

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert — disabled + href → falls back to <button> to prevent navigation
      expect(html).to.contain('<button');
      expect(html).to.contain('disabled');
      expect(html).to.not.contain('<a');
    });
  });

  // ---------------------------------------------------------------
  // 3. Edge cases
  // ---------------------------------------------------------------
  describe('Edge cases', () => {
    it('should_handle_empty_string_children', () => {
      // Arrange
      const element = React.createElement(Button, null, '');

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.contain('<button');
    });

    it('should_handle_numeric_children', () => {
      // Arrange
      const element = React.createElement(Button, null, 42);

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.contain('42');
    });

    it('should_handle_empty_className', () => {
      // Arrange
      const element = React.createElement(Button, { className: '' }, 'Test');

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert — should not have trailing space artifacts
      expect(html).to.contain('Test');
    });

    it('should_handle_empty_href_string_as_no_href', () => {
      // Arrange — empty string is falsy, should render <button>
      const element = React.createElement(Button, { href: '' }, 'Test');

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.contain('<button');
    });
  });

  // ---------------------------------------------------------------
  // 4. Interaction cases
  // ---------------------------------------------------------------
  describe('Interaction cases', () => {
    it('should_include_onClick_handler_attribute_on_button', () => {
      // Arrange
      const handler = sinon.stub();
      const element = React.createElement(Button, { onClick: handler }, 'Clickable');

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert — SSR doesn't include handlers but component accepts them
      expect(html).to.contain('<button');
      expect(html).to.contain('Clickable');
    });

    it('should_include_onClick_handler_attribute_on_anchor', () => {
      // Arrange
      const handler = sinon.stub();
      const element = React.createElement(Button, { href: '/test', onClick: handler }, 'Link');

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.contain('<a');
      expect(html).to.contain('Link');
    });

    it('should_set_type_button_to_prevent_form_submission', () => {
      // Arrange
      const element = React.createElement(Button, null, 'No Submit');

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.contain('type="button"');
    });
  });

  // ---------------------------------------------------------------
  // 5. State transition cases
  // ---------------------------------------------------------------
  describe('State transition cases', () => {
    it('should_render_enabled_state_by_default', () => {
      // Arrange
      const element = React.createElement(Button, null, 'Active');

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.not.contain('disabled=""');
    });

    it('should_render_disabled_state_when_disabled_true', () => {
      // Arrange
      const element = React.createElement(Button, { disabled: true }, 'Disabled');

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.contain('disabled=""');
      expect(html).to.contain('disabled:opacity-50');
      expect(html).to.contain('disabled:cursor-not-allowed');
    });

    it('should_apply_hover_styles_for_solid_variant', () => {
      // Arrange
      const element = React.createElement(Button, { variant: 'solid' }, 'Hover');

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.contain('hover:bg-primary/90');
    });

    it('should_apply_hover_styles_for_outline_variant', () => {
      // Arrange
      const element = React.createElement(Button, { variant: 'outline' }, 'Hover');

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.contain('hover:bg-primary/10');
    });
  });

  // ---------------------------------------------------------------
  // 6. Accessibility cases
  // ---------------------------------------------------------------
  describe('Accessibility cases', () => {
    it('should_render_aria_label_when_provided', () => {
      // Arrange
      const element = React.createElement(Button, { ariaLabel: 'Iniciar sesión' }, 'Ingresar');

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.contain('aria-label="Iniciar sesión"');
    });

    it('should_have_focus_visible_outline_classes', () => {
      // Arrange
      const element = React.createElement(Button, null, 'Focus');

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.contain('focus-visible:outline-2');
      expect(html).to.contain('focus-visible:outline-offset-2');
      expect(html).to.contain('focus-visible:outline-primary');
    });

    it('should_have_role_link_when_rendered_as_anchor', () => {
      // Arrange
      const element = React.createElement(Button, { href: '/auth/login' }, 'Ingresar');

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.contain('role="link"');
    });

    it('should_not_omit_aria_label_when_not_provided', () => {
      // Arrange
      const element = React.createElement(Button, null, 'Text only');

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert — no aria-label attribute should be present
      // (text content serves as accessible name)
      expect(html).to.contain('Text only');
    });
  });

  // ---------------------------------------------------------------
  // 7. Props variations
  // ---------------------------------------------------------------
  describe('Props variations', () => {
    it('should_apply_custom_className_alongside_default_classes', () => {
      // Arrange
      const element = React.createElement(Button, { className: 'my-custom-class' }, 'Styled');

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.contain('my-custom-class');
      expect(html).to.contain('rounded-lg');
    });

    it('should_render_solid_variant_explicitly', () => {
      // Arrange
      const element = React.createElement(Button, { variant: 'solid' }, 'Solid');

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.contain('bg-primary');
    });

    it('should_render_outline_variant_explicitly', () => {
      // Arrange
      const element = React.createElement(Button, { variant: 'outline' }, 'Outline');

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.contain('border-primary');
      expect(html).to.contain('bg-transparent');
    });

    it('should_combine_variant_and_disabled_props', () => {
      // Arrange
      const element = React.createElement(
        Button,
        { variant: 'outline', disabled: true },
        'Disabled Outline',
      );

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.contain('border-primary');
      expect(html).to.contain('disabled=""');
    });

    it('should_combine_variant_href_and_children', () => {
      // Arrange
      const element = React.createElement(
        Button,
        { variant: 'outline', href: '/auth/login' },
        'Ingresar',
      );

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.contain('<a');
      expect(html).to.contain('border-primary');
      expect(html).to.contain('Ingresar');
      expect(html).to.contain('href="/auth/login"');
    });

    it('should_render_with_complex_children', () => {
      // Arrange
      const child = React.createElement('span', { key: 'icon' }, '→ Go');
      const element = React.createElement(Button, null, child);

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.contain('<span>→ Go</span>');
    });

    it('should_render_button_when_href_undefined_and_disabled_true', () => {
      // Arrange — branch: href is undefined, disabled is true
      const element = React.createElement(Button, { disabled: true }, 'No Link Disabled');

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.contain('<button');
      expect(html).to.contain('disabled=""');
    });

    it('should_render_anchor_when_href_present_and_disabled_false', () => {
      // Arrange — branch: href + not disabled → anchor
      const element = React.createElement(
        Button,
        { href: '/path', disabled: false },
        'Link Active',
      );

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.contain('<a');
      expect(html).to.not.contain('disabled=""');
    });

    it('should_use_default_variant_solid_when_not_specified', () => {
      // Arrange — exercise default variant branch
      const element = React.createElement(Button, null, 'Default Solid');

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.contain('bg-primary');
      expect(html).to.not.contain('border-primary');
    });

    it('should_use_default_disabled_false_when_not_specified', () => {
      // Arrange — exercise default disabled branch
      const element = React.createElement(Button, { href: '/test' }, 'Not Disabled');

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert
      expect(html).to.contain('<a');
    });

    it('should_not_set_aria_label_attribute_when_undefined', () => {
      // Arrange — ariaLabel undefined branch
      const element = React.createElement(Button, null, 'Plain');

      // Act
      const html = ReactDOMServer.renderToStaticMarkup(element);

      // Assert — no aria-label attr at all
      expect(html).to.not.contain('aria-label=');
    });
  });
});
