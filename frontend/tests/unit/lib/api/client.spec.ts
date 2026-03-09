/**
 * @fileoverview Tests for the API client module.
 *
 * Covers the `apiClient` function: success paths, error mapping,
 * and edge cases.
 *
 * @remarks
 * Pattern: AAA (Arrange-Act-Assert).
 * Naming: should_<expected>_when_<condition>.
 */

import { expect } from 'chai';
import sinon from 'sinon';
import { apiClient, type ApiError } from '../../../../src/lib/api/client';

describe('apiClient', () => {
  let fetchStub: sinon.SinonStub;

  beforeEach(() => {
    fetchStub = sinon.stub(globalThis, 'fetch');
  });

  afterEach(() => {
    sinon.restore();
  });

  // ---------------------------------------------------------------
  // 1. Positive cases
  // ---------------------------------------------------------------
  describe('Positive cases', () => {
    it('should_return_parsed_json_when_response_ok', async () => {
      // Arrange
      fetchStub.resolves({
        ok: true,
        json: sinon.stub().resolves({ id: '123' }),
      });

      // Act
      const result = await apiClient('/auth/register', {
        method: 'POST',
        body: JSON.stringify({ phone: '+573001234567' }),
      });

      // Assert
      expect(result).to.deep.equal({ id: '123' });
    });

    it('should_set_content_type_json_header', async () => {
      // Arrange
      fetchStub.resolves({
        ok: true,
        json: sinon.stub().resolves({}),
      });

      // Act
      await apiClient('/test');

      // Assert
      const [, init] = fetchStub.firstCall.args;
      expect(init.headers['Content-Type']).to.equal('application/json');
    });

    it('should_prepend_base_url', async () => {
      // Arrange
      fetchStub.resolves({ ok: true, json: sinon.stub().resolves({}) });

      // Act
      await apiClient('/auth/register');

      // Assert
      const [url] = fetchStub.firstCall.args;
      expect(url).to.contain('/auth/register');
    });
  });

  // ---------------------------------------------------------------
  // 2. Negative cases
  // ---------------------------------------------------------------
  describe('Negative cases', () => {
    it('should_throw_api_error_when_response_not_ok', async () => {
      // Arrange
      fetchStub.resolves({
        ok: false,
        status: 409,
        json: sinon.stub().resolves({ detail: 'Phone exists' }),
      });

      // Act & Assert
      try {
        await apiClient('/auth/register');
        expect.fail('Should have thrown');
      } catch (err) {
        const apiErr = err as ApiError;
        expect(apiErr.status).to.equal(409);
        expect(apiErr.detail).to.deep.equal({ detail: 'Phone exists' });
      }
    });

    it('should_handle_non_json_error_body', async () => {
      // Arrange
      fetchStub.resolves({
        ok: false,
        status: 500,
        json: sinon.stub().rejects(new Error('not json')),
      });

      // Act & Assert
      try {
        await apiClient('/auth/register');
        expect.fail('Should have thrown');
      } catch (err) {
        const apiErr = err as ApiError;
        expect(apiErr.status).to.equal(500);
        expect(apiErr.detail).to.be.undefined;
      }
    });

    it('should_throw_when_fetch_itself_rejects', async () => {
      // Arrange
      fetchStub.rejects(new Error('Network error'));

      // Act & Assert
      try {
        await apiClient('/auth/register');
        expect.fail('Should have thrown');
      } catch (err) {
        expect((err as Error).message).to.equal('Network error');
      }
    });
  });

  // ---------------------------------------------------------------
  // 3. Edge cases
  // ---------------------------------------------------------------
  describe('Edge cases', () => {
    it('should_merge_custom_headers_with_defaults', async () => {
      // Arrange
      fetchStub.resolves({ ok: true, json: sinon.stub().resolves({}) });

      // Act
      await apiClient('/test', {
        headers: { Authorization: 'Bearer token' },
      });

      // Assert
      const [, init] = fetchStub.firstCall.args;
      expect(init.headers['Content-Type']).to.equal('application/json');
      expect(init.headers['Authorization']).to.equal('Bearer token');
    });

    it('should_handle_empty_path', async () => {
      // Arrange
      fetchStub.resolves({ ok: true, json: sinon.stub().resolves({}) });

      // Act
      await apiClient('');

      // Assert
      const [url] = fetchStub.firstCall.args;
      expect(url).to.be.a('string');
    });
  });

  // ---------------------------------------------------------------
  // 4. Interaction cases
  // ---------------------------------------------------------------
  describe('Interaction cases', () => {
    it('should_forward_method_and_body', async () => {
      // Arrange
      fetchStub.resolves({ ok: true, json: sinon.stub().resolves({}) });
      const body = JSON.stringify({ phone: '+573001234567' });

      // Act
      await apiClient('/auth/register', { method: 'POST', body });

      // Assert
      const [, init] = fetchStub.firstCall.args;
      expect(init.method).to.equal('POST');
      expect(init.body).to.equal(body);
    });
  });

  // ---------------------------------------------------------------
  // 5. State transition cases
  // ---------------------------------------------------------------
  describe('State transition cases', () => {
    it('should_include_error_message_in_thrown_ApiError', async () => {
      // Arrange
      fetchStub.resolves({
        ok: false,
        status: 422,
        json: sinon.stub().resolves({ detail: [{ msg: 'Invalid phone' }] }),
      });

      // Act & Assert
      try {
        await apiClient('/auth/register');
        expect.fail('Should have thrown');
      } catch (err) {
        const apiErr = err as ApiError;
        expect(apiErr.message).to.equal('Request failed with status 422');
      }
    });
  });

  // ---------------------------------------------------------------
  // 6. Accessibility cases (N/A — no UI)
  // ---------------------------------------------------------------

  // ---------------------------------------------------------------
  // 7. Props variations
  // ---------------------------------------------------------------
  describe('Props variations', () => {
    it('should_work_without_init_parameter', async () => {
      // Arrange
      fetchStub.resolves({ ok: true, json: sinon.stub().resolves({ ok: true }) });

      // Act
      const result = await apiClient('/health');

      // Assert
      expect(result).to.deep.equal({ ok: true });
    });
  });
});
