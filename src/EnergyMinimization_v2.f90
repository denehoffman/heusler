program EnergyMinimization
    implicit none
    character (16), dimension (:), allocatable :: configs
    character (64) :: enum_file, int_file
    character (5) :: buffer
    character (16) :: config, config_best
    integer, dimension (:), allocatable :: ids
    integer :: n, j, k, numlines = 0, header = 0, steps = 201, id_best
    real, dimension(4, 4, 2) :: intmatrix = 0
    real :: E = 0, E_best
    real, dimension (:), allocatable :: intvals

    call getarg(1, enum_file)
    call getarg(2, int_file)
    open(1, file=enum_file)
    do
        read(1, *, end=1001)
        numlines = numlines + 1
    end do
    1001 close(1)
    open(1, file=enum_file)
    do while(buffer /= 'start')
        read(1, *) buffer
        header = header + 1
    end do
    allocate(configs(numlines - header))
    allocate(ids(numlines - header))
    do n = 1, numlines - header
        read(1, *) ids(n), buffer, buffer, buffer, buffer, &
            buffer, buffer, buffer, buffer, buffer, &
            buffer, buffer, buffer, buffer, buffer, &
            buffer, buffer, buffer, buffer, buffer, &
            buffer, buffer, buffer, buffer, buffer, &
            buffer, configs(n)
    end do
    close(1)
    allocate(intvals(steps))
    call linspace(intvals, -1, 1, steps)
    do j = 1, size(intvals)
        do k = 1, size(intvals)
            intmatrix(1, 1, 1) = intvals(j)
            intmatrix(2, 2, 1) = intvals(j)
            intmatrix(3, 3, 1) = intvals(j)
            intmatrix(4, 4, 1) = intvals(j)
            intmatrix(1, 1, 2) = intvals(k)
            intmatrix(2, 2, 2) = intvals(k)
            intmatrix(3, 3, 2) = intvals(k)
            intmatrix(4, 4, 2) = intvals(k)
            E_best = 0
            call getEnergy(configs(5), int_file, E_best, intmatrix)
            id_best = 5
            do n = 1, size(configs)
                config = configs(n)
                E = 0
                call getEnergy(config, int_file, E, intmatrix)
                if (E <= E_best) then
                    E_best = E
                    config_best = config
                    id_best = ids(n)
                end if
            end do
            write(*, fmt="(i6a1)", advance="no") id_best, ","
        end do
        write(*, *)
    end do
    deallocate(intvals)
    deallocate(configs)
    deallocate(ids)
end program

subroutine linspace(z, l, k, n)
    implicit none
    real, dimension(n) :: z
    integer :: l, k, n, i
    real :: d, x, y
    x = float(k)
    y = float(l)
    d = (x - y) / n
    z(1) = float(l)
    do i = 2, n - 1
        z(i) = z(i-1) + d
    end do
    z(1) = y
    z(n) = x
    return
end subroutine

subroutine getEnergy(config, int_file, E, intmatrix)
    implicit none
    character (64), intent(in) :: int_file
    character (16), intent(in) :: config
    real, intent(out) :: E
    integer :: posa, posb, dist, sa, sb
    real, dimension(4, 4, 2) :: intmatrix
    open(1, file=int_file)
    do
        read(1, *, end=1002) posa, posb, dist
        read(config(posa:posa), *) sa
        read(config(posb:posb), *) sb
        E = E + intmatrix(sa, sb, dist)
    end do
    1002 close(1)

end subroutine
