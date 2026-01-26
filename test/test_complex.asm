; Generated 6502 Assembly Code
; Processor: 6502

    processor 6502
    org $0600    ; Start program at $0600

start:
    LDX #$FF
    TXS          ; Initialize stack pointer

    ; var y = <expression>
    LDA #$01      ; Load literal 1
    STA $10        ; Store to y

    ; var z = <expression>
    LDA #$02      ; Load literal 2
    STA $11        ; Store to z

    ; var x = <expression>
    LDA #$05      ; Load literal 5
    PHA             ; Save left operand
    LDA #$04      ; Load literal 4
    PHA             ; Save left operand
    LDA $10        ; Load y
    PHA             ; Save left operand
    LDA $11        ; Load z
    EOR #$FF        ; One's complement
    CLC
    ADC #1          ; Two's complement (negate)
    STA $FE         ; Save right operand
    PLA             ; Restore left operand
    SEC
    SBC $FE         ; Subtract
    TAY             ; Save right in Y
    PLA             ; Get left
    CMP #0
    BNE OR_T0    ; Left is true
    TYA             ; Check right
    CMP #0
    BNE OR_T0    ; Right is true
    JMP OR_F1
OR_T0:
    LDA #1          ; At least one true
    JMP OR_E2
OR_F1:
    LDA #0          ; Both false
OR_E2:
    STA $FE         ; Save right operand
    PLA             ; Restore left operand
    CLC
    ADC $FE         ; Add
    PHA             ; Save left operand
    LDA #$03      ; Load literal 3
    STA $FE         ; Save right operand
    PLA             ; Restore left operand
    CLC
    ADC $FE         ; Add
    PHA             ; Save left operand
    LDA #$04      ; Load literal 4
    EOR #$FF        ; One's complement
    CLC
    ADC #1          ; Two's complement (negate)
    STA $FE         ; Save right operand
    PLA             ; Restore left operand
    CLC
    ADC $FE         ; Add
    PHA             ; Save left operand
    LDA #$0A      ; Load literal 10
    STA $FE         ; Save right operand
    PLA             ; Restore left operand
    ORA $FE         ; Bitwise OR
    STA $12        ; Store to x

    ; output(<value>)
    LDA $12        ; Load x
    JSR output_routine


    BRK          ; End program

; ==================== I/O Routines ====================

; Target: py65mon emulator
; Console output at $F001, blocking input at $F005

output_routine:
    ; Output value in A as decimal number (0-255)
    ; Uses zero-page $FB-$FD for temporary storage
    STA $FB          ; Store number to output
    LDA #1
    STA $FD          ; Start suppressing leading zeros

    ; Output hundreds digit
    LDA $FB
    LDX #0           ; X will count hundreds
output_hundreds:
    CMP #100
    BCC output_hundreds_done
    SBC #100         ; Subtract 100 (carry is set)
    INX
    JMP output_hundreds
output_hundreds_done:
    STA $FB          ; Save remainder
    TXA
    BEQ skip_hundreds ; Skip if zero
    LDA #0
    STA $FD          ; Found non-zero, stop suppressing
    TXA
    CLC
    ADC #48          ; Convert to ASCII
    STA $F001        ; Output hundreds digit
skip_hundreds:

    ; Output tens digit
    LDA $FB
    LDX #0           ; X will count tens
output_tens:
    CMP #10
    BCC output_tens_done
    SBC #10          ; Subtract 10 (carry is set)
    INX
    JMP output_tens
output_tens_done:
    STA $FB          ; Save remainder (ones digit)
    TXA
    BNE print_tens   ; Print if non-zero
    LDA $FD
    BNE skip_tens    ; Skip if still suppressing zeros
print_tens:
    LDA #0
    STA $FD          ; Stop suppressing
    TXA
    CLC
    ADC #48          ; Convert to ASCII
    STA $F001        ; Output tens digit
skip_tens:

    ; Output ones digit (always output, even if zero)
    LDA $FB
    CLC
    ADC #48          ; Convert to ASCII
    STA $F001        ; Output ones digit

    ; Output newline
    LDA #10
    STA $F001
    RTS

input_routine:
    ; Read multi-digit number from console until Enter
    ; Result stored in accumulator (0-255 max)
    ; Uses zero-page $FA for accumulating result
    LDA #0
    STA $FA         ; Initialize result to 0

input_loop:
    ; Wait for next character
input_wait:
    LDA $F004       ; Poll for input
    BEQ input_wait  ; Keep waiting if no key pressed

    ; Check if Enter key (ASCII 10 or 13)
    CMP #10
    BEQ input_done  ; If Enter (LF), we're done
    CMP #13
    BEQ input_done  ; If Enter (CR), we're done

    ; Convert ASCII digit to number (subtract 48)
    SEC
    SBC #48
    STA $FE         ; Store new digit in $FE

    ; Multiply current result by 10
    ; result = result * 10 + new_digit
    LDA $FA         ; Load current result
    STA $FD         ; Save copy
    ASL             ; result * 2
    ASL             ; result * 4
    CLC
    ADC $FD         ; result * 4 + result * 1 = result * 5
    ASL             ; result * 10
    CLC
    ADC $FE         ; Add new digit
    STA $FA         ; Store updated result

    JMP input_loop  ; Read next character

input_done:
    LDA $FA         ; Load final result into A
    RTS
